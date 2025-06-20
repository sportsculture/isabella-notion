"""
Basic tests for Isabella Notion
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.config import Settings, validate_environment
from core.conversation_analyzer import ConversationAnalyzer

class TestConfig:
    """Test configuration module"""
    
    def test_settings_default_values(self):
        """Test that settings have appropriate default values"""
        # Mock environment to avoid requiring actual API keys
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            settings = Settings()
            assert settings.APP_HOST == "localhost"
            assert settings.APP_PORT == 8000
            assert settings.DEBUG == True
            assert settings.OPENAI_MODEL == "gpt-4"
    
    def test_validate_environment_missing_key(self):
        """Test environment validation with missing API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables"):
                validate_environment()

class TestConversationAnalyzer:
    """Test conversation analysis functionality"""
    
    @pytest.fixture
    def sample_conversation(self):
        """Sample conversation for testing"""
        return """
        Hey, I want help with my YouTube channel. I want to be more consistent and 
        plan better. I want dreamy, colorful content with a kawaii aesthetic. 
        I need a content calendar, filming checklist, and analytics tracker.
        """
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        analyzer = ConversationAnalyzer()
        
        # Test with messy text
        messy_text = "Hello   world!\n\n\nThis  has   extra    spaces."
        cleaned = analyzer._preprocess_text(messy_text)
        
        assert "   " not in cleaned
        assert cleaned.count(' ') < messy_text.count(' ')
    
    def test_build_analysis_prompt(self):
        """Test analysis prompt building"""
        analyzer = ConversationAnalyzer()
        conversation = "I need a content calendar for my YouTube channel"
        
        prompt = analyzer._build_analysis_prompt(conversation)
        
        assert "JSON object" in prompt
        assert "topics" in prompt
        assert "planning_elements" in prompt
        assert conversation in prompt
    
    def test_parse_analysis_response_valid_json(self):
        """Test parsing valid JSON response"""
        analyzer = ConversationAnalyzer()
        
        valid_json = '''
        {
            "topics": ["YouTube", "Content Creation"],
            "planning_elements": {
                "schedules": ["Weekly uploads"],
                "checklists": ["Filming checklist"],
                "trackers": ["View tracker"],
                "workflows": ["Upload process"]
            },
            "user_preferences": {
                "aesthetic_style": ["dreamy", "colorful"],
                "colors": ["pink", "purple"],
                "organization_style": ["visual"],
                "features_requested": ["calendar", "tracker"]
            },
            "action_items": ["Create content calendar"],
            "structure": {
                "main_categories": ["Content", "Analytics"],
                "database_types": ["content_calendar"],
                "view_types": ["calendar", "kanban"],
                "page_types": ["dashboard"]
            }
        }
        '''
        
        result = analyzer._parse_analysis_response(valid_json)
        
        assert "topics" in result
        assert "YouTube" in result["topics"]
        assert result["user_preferences"]["aesthetic_style"] == ["dreamy", "colorful"]
    
    def test_parse_analysis_response_invalid_json(self):
        """Test parsing invalid JSON falls back gracefully"""
        analyzer = ConversationAnalyzer()
        
        invalid_response = "This is not JSON at all!"
        result = analyzer._parse_analysis_response(invalid_response)
        
        # Should return default structure
        assert "topics" in result
        assert isinstance(result["topics"], list)
        assert "planning_elements" in result

@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Test async functionality with mocked APIs"""
    
    async def test_conversation_analyzer_with_mock(self):
        """Test conversation analyzer with mocked OpenAI API"""
        
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "topics": ["Test Topic"],
            "planning_elements": {
                "schedules": [],
                "checklists": [],
                "trackers": [],
                "workflows": []
            },
            "user_preferences": {
                "aesthetic_style": [],
                "colors": [],
                "organization_style": [],
                "features_requested": []
            },
            "action_items": [],
            "structure": {
                "main_categories": ["Test"],
                "database_types": ["test_db"],
                "view_types": ["table"],
                "page_types": ["page"]
            }
        }
        '''
        
        with patch('core.conversation_analyzer.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            analyzer = ConversationAnalyzer()
            result = await analyzer.analyze("Test conversation")
            
            assert result["topics"] == ["Test Topic"]
            assert result["structure"]["main_categories"] == ["Test"]