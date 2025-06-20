"""
Enhanced tests for the modular conversation analyzer
Tests all the new extraction functions and parallel execution
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.conversation_analyzer import ConversationAnalyzer


class TestIndividualExtractionFunctions:
    """Test each individual extraction function in isolation"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance with mocked OpenAI client"""
        with patch('core.conversation_analyzer.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            return ConversationAnalyzer()
    
    @pytest.fixture
    def sample_conversation(self):
        """Sample conversation for testing individual functions"""
        return """
        Hi, I need help with my creative business. I want to create a dreamy, 
        colorful workspace with pastel colors like pink and lavender. 
        I need to track my projects, schedule content creation, and manage 
        my art supplies inventory. I'd like a content calendar, task tracker, 
        and a gallery view for my artwork. Can you help me create workflows 
        for my daily routines and weekly planning?
        """
    
    @pytest.mark.asyncio
    async def test_extract_topics_success(self, analyzer, sample_conversation):
        """Test successful topic extraction"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '["Creative Business", "Art Projects", "Content Creation", "Workspace Organization"]'
        
        analyzer.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        topics = await analyzer.extract_topics(sample_conversation)
        
        assert isinstance(topics, list)
        assert len(topics) == 4
        assert "Creative Business" in topics
        assert "Art Projects" in topics
        
        # Verify the API was called correctly
        analyzer.client.chat.completions.create.assert_called_once()
        call_args = analyzer.client.chat.completions.create.call_args
        assert call_args[1]['model'] == analyzer.settings.OPENAI_MODEL
        assert call_args[1]['temperature'] == 0.2
        assert sample_conversation in call_args[1]['messages'][1]['content']
    
    @pytest.mark.asyncio
    async def test_extract_topics_api_error(self, analyzer, sample_conversation):
        """Test topic extraction with API error - should return fallback"""
        analyzer.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        topics = await analyzer.extract_topics(sample_conversation)
        
        assert isinstance(topics, list)
        assert topics == ["General Planning"]
    
    @pytest.mark.asyncio
    async def test_extract_topics_invalid_json(self, analyzer, sample_conversation):
        """Test topic extraction with invalid JSON response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'Not valid JSON at all!'
        
        analyzer.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        topics = await analyzer.extract_topics(sample_conversation)
        
        assert isinstance(topics, list)
        assert topics == ["General Planning"]
    
    @pytest.mark.asyncio
    async def test_identify_planning_elements_success(self, analyzer, sample_conversation):
        """Test successful planning elements identification"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "schedules": ["Daily art practice", "Weekly content creation"],
            "checklists": ["Art supplies inventory", "Project completion checklist"],
            "trackers": ["Project progress tracker", "Time tracking"],
            "workflows": ["Morning routine", "Content creation workflow"]
        })
        
        analyzer.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        elements = await analyzer.identify_planning_elements(sample_conversation)
        
        assert isinstance(elements, dict)
        assert "schedules" in elements
        assert "checklists" in elements
        assert "trackers" in elements
        assert "workflows" in elements
        
        assert len(elements["schedules"]) == 2
        assert "Daily art practice" in elements["schedules"]
        assert "Art supplies inventory" in elements["checklists"]
        assert "Project progress tracker" in elements["trackers"]
        assert "Morning routine" in elements["workflows"]
    
    @pytest.mark.asyncio
    async def test_identify_planning_elements_error(self, analyzer, sample_conversation):
        """Test planning elements identification with error - should return empty structure"""
        analyzer.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        elements = await analyzer.identify_planning_elements(sample_conversation)
        
        assert isinstance(elements, dict)
        assert elements == {"schedules": [], "checklists": [], "trackers": [], "workflows": []}
    
    @pytest.mark.asyncio
    async def test_detect_user_preferences_success(self, analyzer, sample_conversation):
        """Test successful user preferences detection"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "aesthetic_style": ["dreamy", "colorful", "artistic"],
            "colors": ["pink", "lavender", "pastel"],
            "organization_style": ["visual", "categorized", "project-based"],
            "features_requested": ["content calendar", "task tracker", "gallery view"]
        })
        
        analyzer.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        preferences = await analyzer.detect_user_preferences(sample_conversation)
        
        assert isinstance(preferences, dict)
        assert "aesthetic_style" in preferences
        assert "colors" in preferences
        assert "organization_style" in preferences
        assert "features_requested" in preferences
        
        assert "dreamy" in preferences["aesthetic_style"]
        assert "pink" in preferences["colors"]
        assert "visual" in preferences["organization_style"]
        assert "content calendar" in preferences["features_requested"]
    
    @pytest.mark.asyncio
    async def test_detect_user_preferences_error(self, analyzer, sample_conversation):
        """Test user preferences detection with error"""
        analyzer.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        preferences = await analyzer.detect_user_preferences(sample_conversation)
        
        expected = {"aesthetic_style": [], "colors": [], "organization_style": [], "features_requested": []}
        assert preferences == expected
    
    @pytest.mark.asyncio
    async def test_extract_action_items_success(self, analyzer, sample_conversation):
        """Test successful action items extraction"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '["Create content calendar", "Set up task tracker", "Organize art supplies", "Establish daily routine"]'
        
        analyzer.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        action_items = await analyzer.extract_action_items(sample_conversation)
        
        assert isinstance(action_items, list)
        assert len(action_items) == 4
        assert "Create content calendar" in action_items
        assert "Set up task tracker" in action_items
    
    @pytest.mark.asyncio
    async def test_extract_action_items_error(self, analyzer, sample_conversation):
        """Test action items extraction with error"""
        analyzer.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        action_items = await analyzer.extract_action_items(sample_conversation)
        
        assert isinstance(action_items, list)
        assert action_items == []
    
    @pytest.mark.asyncio
    async def test_extract_structure_success(self, analyzer, sample_conversation):
        """Test successful structure extraction"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "main_categories": ["Creative Projects", "Business Management", "Content Creation"],
            "database_types": ["project_tracker", "content_calendar", "inventory_manager"],
            "view_types": ["gallery", "calendar", "kanban", "table"],
            "page_types": ["dashboard", "project_templates", "resource_library"]
        })
        
        analyzer.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        structure = await analyzer.extract_structure(sample_conversation)
        
        assert isinstance(structure, dict)
        assert "main_categories" in structure
        assert "database_types" in structure
        assert "view_types" in structure
        assert "page_types" in structure
        
        assert "Creative Projects" in structure["main_categories"]
        assert "project_tracker" in structure["database_types"]
        assert "gallery" in structure["view_types"]
        assert "dashboard" in structure["page_types"]
    
    @pytest.mark.asyncio
    async def test_extract_structure_error(self, analyzer, sample_conversation):
        """Test structure extraction with error - should return default structure"""
        analyzer.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        structure = await analyzer.extract_structure(sample_conversation)
        
        expected = {
            "main_categories": ["Planning"],
            "database_types": ["task_tracker"],
            "view_types": ["table", "calendar"],
            "page_types": ["dashboard"]
        }
        assert structure == expected


class TestParallelExecution:
    """Test the parallel execution of extraction functions"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer with mocked client"""
        with patch('core.conversation_analyzer.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            return ConversationAnalyzer()
    
    @pytest.fixture
    def mock_responses(self):
        """Mock responses for all extraction functions"""
        return {
            'topics': '["Test Topic 1", "Test Topic 2"]',
            'planning_elements': json.dumps({
                "schedules": ["Test schedule"],
                "checklists": ["Test checklist"],
                "trackers": ["Test tracker"],
                "workflows": ["Test workflow"]
            }),
            'user_preferences': json.dumps({
                "aesthetic_style": ["minimal"],
                "colors": ["blue"],
                "organization_style": ["structured"],
                "features_requested": ["calendar"]
            }),
            'action_items': '["Test action 1", "Test action 2"]',
            'structure': json.dumps({
                "main_categories": ["Test Category"],
                "database_types": ["test_db"],
                "view_types": ["table"],
                "page_types": ["dashboard"]
            })
        }
    
    @pytest.mark.asyncio
    async def test_parallel_execution_success(self, analyzer, mock_responses):
        """Test that all extraction functions are called in parallel"""
        # Create a mock that returns different responses based on prompt content
        def mock_create(*args, **kwargs):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            
            # Determine which function is being called based on the prompt
            prompt = kwargs['messages'][1]['content']
            if 'extract the main topics' in prompt.lower():
                mock_response.choices[0].message.content = mock_responses['topics']
            elif 'extract planning elements' in prompt.lower():
                mock_response.choices[0].message.content = mock_responses['planning_elements']
            elif 'extract user preferences' in prompt.lower():
                mock_response.choices[0].message.content = mock_responses['user_preferences']
            elif 'extract concrete action items' in prompt.lower():
                mock_response.choices[0].message.content = mock_responses['action_items']
            elif 'organizational structure' in prompt.lower():
                mock_response.choices[0].message.content = mock_responses['structure']
            else:
                mock_response.choices[0].message.content = '[]'
            
            return mock_response
        
        analyzer.client.chat.completions.create = AsyncMock(side_effect=mock_create)
        
        conversation = "Test conversation for parallel execution"
        
        # Time the execution
        start_time = time.time()
        result = await analyzer.analyze(conversation)
        execution_time = time.time() - start_time
        
        # Verify all functions were called (5 times total)
        assert analyzer.client.chat.completions.create.call_count == 5
        
        # Verify the result structure
        assert "topics" in result
        assert "planning_elements" in result
        assert "user_preferences" in result
        assert "action_items" in result
        assert "structure" in result
        
        # Verify the content is correct
        assert result["topics"] == ["Test Topic 1", "Test Topic 2"]
        assert result["planning_elements"]["schedules"] == ["Test schedule"]
        assert result["user_preferences"]["aesthetic_style"] == ["minimal"]
        assert result["action_items"] == ["Test action 1", "Test action 2"]
        assert result["structure"]["main_categories"] == ["Test Category"]
        
        # Execution should be reasonably fast (parallel execution)
        assert execution_time < 10  # Should complete within 10 seconds
    
    @pytest.mark.asyncio
    async def test_parallel_execution_with_one_failure(self, analyzer, mock_responses):
        """Test parallel execution when one function fails"""
        call_count = 0
        
        def mock_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            
            # Make the topics extraction fail
            prompt = kwargs['messages'][1]['content']
            if 'extract the main topics' in prompt.lower():
                raise Exception("Simulated API failure")
            elif 'extract planning elements' in prompt.lower():
                mock_response.choices[0].message.content = mock_responses['planning_elements']
            elif 'extract user preferences' in prompt.lower():
                mock_response.choices[0].message.content = mock_responses['user_preferences']
            elif 'extract concrete action items' in prompt.lower():
                mock_response.choices[0].message.content = mock_responses['action_items']
            elif 'organizational structure' in prompt.lower():
                mock_response.choices[0].message.content = mock_responses['structure']
            else:
                mock_response.choices[0].message.content = '[]'
            
            return mock_response
        
        analyzer.client.chat.completions.create = AsyncMock(side_effect=mock_create)
        
        conversation = "Test conversation for partial failure"
        result = await analyzer.analyze(conversation)
        
        # Should still return a complete result structure
        assert "topics" in result
        assert "planning_elements" in result
        assert "user_preferences" in result
        assert "action_items" in result
        assert "structure" in result
        
        # Topics should fall back to default due to error
        assert result["topics"] == ["General Planning"]
        
        # Other functions should work normally
        assert result["planning_elements"]["schedules"] == ["Test schedule"]
        assert result["user_preferences"]["aesthetic_style"] == ["minimal"]


class TestWithSeedConversation:
    """Test analyzer with real seed conversation data"""
    
    @pytest.fixture
    def seed_conversation(self):
        """Load the seed conversation data"""
        seed_path = Path(__file__).parent.parent / "seed-convo.txt"
        if seed_path.exists():
            with open(seed_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Fallback sample if seed file doesn't exist
            return """
            Hey, I want help with my YouTube channel because I wanna be more consistent.
            I wanna make my videos more cinematic, especially my shorts. My goal is for this 
            channel to document my art journey. I want dreamy, colorful content with a kawaii 
            aesthetic. I need help with planning, content calendar, and analytics tracking.
            """
    
    @pytest.fixture
    def analyzer_with_realistic_mocks(self):
        """Create analyzer with realistic mock responses"""
        with patch('core.conversation_analyzer.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            def mock_create(*args, **kwargs):
                mock_response = Mock()
                mock_response.choices = [Mock()]
                
                prompt = kwargs['messages'][1]['content']
                
                if 'extract the main topics' in prompt.lower():
                    mock_response.choices[0].message.content = json.dumps([
                        "YouTube Content Creation", "Art Journey Documentation", 
                        "Cinematic Video Production", "Content Planning", "Analytics Tracking"
                    ])
                elif 'extract planning elements' in prompt.lower():
                    mock_response.choices[0].message.content = json.dumps({
                        "schedules": ["Weekly video uploads", "Daily art practice", "Content planning sessions"],
                        "checklists": ["Video filming checklist", "Equipment setup", "Editing workflow"],
                        "trackers": ["Analytics dashboard", "Subscriber growth", "Engagement metrics"],
                        "workflows": ["Content creation workflow", "Filming process", "Upload schedule"]
                    })
                elif 'extract user preferences' in prompt.lower():
                    mock_response.choices[0].message.content = json.dumps({
                        "aesthetic_style": ["dreamy", "cinematic", "kawaii", "colorful"],
                        "colors": ["pastel", "pink", "soft tones"],
                        "organization_style": ["visual", "calendar-based", "project-oriented"],
                        "features_requested": ["content calendar", "analytics tracker", "filming checklist"]
                    })
                elif 'extract concrete action items' in prompt.lower():
                    mock_response.choices[0].message.content = json.dumps([
                        "Create content calendar", "Set up analytics tracking", 
                        "Develop filming checklist", "Plan video series", "Organize equipment"
                    ])
                elif 'organizational structure' in prompt.lower():
                    mock_response.choices[0].message.content = json.dumps({
                        "main_categories": ["Content Creation", "Analytics", "Art Documentation", "Planning"],
                        "database_types": ["content_calendar", "video_tracker", "analytics_dashboard", "equipment_inventory"],
                        "view_types": ["calendar", "gallery", "kanban", "table"],
                        "page_types": ["dashboard", "templates", "archive", "inspiration_board"]
                    })
                else:
                    mock_response.choices[0].message.content = '[]'
                
                return mock_response
            
            mock_client.chat.completions.create = AsyncMock(side_effect=mock_create)
            return ConversationAnalyzer()
    
    @pytest.mark.asyncio
    async def test_seed_conversation_analysis(self, analyzer_with_realistic_mocks, seed_conversation):
        """Test analysis with the actual seed conversation"""
        result = await analyzer_with_realistic_mocks.analyze(seed_conversation)
        
        # Verify structure
        assert isinstance(result, dict)
        required_keys = ["topics", "planning_elements", "user_preferences", "action_items", "structure"]
        for key in required_keys:
            assert key in result
        
        # Verify topics
        assert isinstance(result["topics"], list)
        assert len(result["topics"]) > 0
        assert any("YouTube" in topic for topic in result["topics"])
        
        # Verify planning elements
        planning = result["planning_elements"]
        assert isinstance(planning, dict)
        assert "schedules" in planning
        assert "checklists" in planning
        assert "trackers" in planning
        assert "workflows" in planning
        
        # Verify user preferences
        preferences = result["user_preferences"]
        assert isinstance(preferences, dict)
        assert "aesthetic_style" in preferences
        assert "colors" in preferences
        assert any("dreamy" in style for style in preferences["aesthetic_style"])
        
        # Verify action items
        assert isinstance(result["action_items"], list)
        assert len(result["action_items"]) > 0
        
        # Verify structure
        structure = result["structure"]
        assert isinstance(structure, dict)
        assert "main_categories" in structure
        assert "database_types" in structure
        assert "view_types" in structure
        assert "page_types" in structure
    
    @pytest.mark.asyncio
    async def test_preprocessed_text_with_seed_conversation(self, analyzer_with_realistic_mocks, seed_conversation):
        """Test that text preprocessing works correctly with seed conversation"""
        analyzer = analyzer_with_realistic_mocks
        
        # Test preprocessing
        cleaned_text = analyzer._preprocess_text(seed_conversation)
        
        # Should not have excessive whitespace
        assert "  " not in cleaned_text or cleaned_text.count("  ") < seed_conversation.count("  ")
        
        # Should be properly cleaned
        assert len(cleaned_text) <= len(seed_conversation)
        assert cleaned_text.strip() == cleaned_text


class TestErrorHandlingAndFallbacks:
    """Test comprehensive error handling and fallback mechanisms"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer with mocked client"""
        with patch('core.conversation_analyzer.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            return ConversationAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_with_all_functions_failing(self, analyzer):
        """Test main analyze function when all sub-functions fail"""
        # Make all API calls fail
        analyzer.client.chat.completions.create = AsyncMock(side_effect=Exception("Complete API failure"))
        
        conversation = "This should fail gracefully"
        result = await analyzer.analyze(conversation)
        
        # Should still return a valid structure with fallback values
        assert isinstance(result, dict)
        
        # Check fallback values
        assert result["topics"] == ["General Planning"]
        assert result["planning_elements"] == {"schedules": [], "checklists": [], "trackers": [], "workflows": []}
        assert result["user_preferences"] == {"aesthetic_style": [], "colors": [], "organization_style": [], "features_requested": []}
        assert result["action_items"] == []
        assert result["structure"]["main_categories"] == ["Planning"]
    
    @pytest.mark.asyncio
    async def test_analyze_with_network_timeout(self, analyzer):
        """Test analyzer behavior with network timeout"""
        import asyncio
        
        # Simulate timeout
        analyzer.client.chat.completions.create = AsyncMock(side_effect=asyncio.TimeoutError("Request timeout"))
        
        conversation = "Test timeout handling"
        result = await analyzer.analyze(conversation)
        
        # Should handle timeout gracefully and return fallback values
        assert isinstance(result, dict)
        assert "topics" in result
        assert "planning_elements" in result
    
    @pytest.mark.asyncio
    async def test_malformed_json_responses(self, analyzer):
        """Test handling of malformed JSON responses"""
        def mock_create(*args, **kwargs):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            
            # Return malformed JSON
            prompt = kwargs['messages'][1]['content']
            if 'extract the main topics' in prompt.lower():
                mock_response.choices[0].message.content = '["topic1", "topic2"'  # Missing closing bracket
            elif 'extract planning elements' in prompt.lower():
                mock_response.choices[0].message.content = '{"schedules": ["test"]'  # Incomplete JSON
            else:
                mock_response.choices[0].message.content = 'Not JSON at all!'
            
            return mock_response
        
        analyzer.client.chat.completions.create = AsyncMock(side_effect=mock_create)
        
        conversation = "Test malformed JSON handling"
        result = await analyzer.analyze(conversation)
        
        # Should handle malformed JSON gracefully
        assert isinstance(result, dict)
        assert result["topics"] == ["General Planning"]  # Fallback
        assert result["planning_elements"] == {"schedules": [], "checklists": [], "trackers": [], "workflows": []}  # Fallback
    
    @pytest.mark.asyncio
    async def test_empty_conversation_input(self, analyzer):
        """Test analyzer with empty conversation input"""
        # Mock successful but empty responses
        def mock_create(*args, **kwargs):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '[]'
            return mock_response
        
        analyzer.client.chat.completions.create = AsyncMock(side_effect=mock_create)
        
        result = await analyzer.analyze("")
        
        # Should still return valid structure
        assert isinstance(result, dict)
        assert "topics" in result
        assert "planning_elements" in result
        assert "user_preferences" in result
        assert "action_items" in result
        assert "structure" in result


class TestPerformanceAndBenchmarking:
    """Test performance characteristics of the enhanced analyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer with fast mock responses"""
        with patch('core.conversation_analyzer.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Fast mock responses
            def mock_create(*args, **kwargs):
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = '[]'
                return mock_response
            
            mock_client.chat.completions.create = AsyncMock(side_effect=mock_create)
            return ConversationAnalyzer()
    
    @pytest.mark.asyncio
    async def test_parallel_vs_sequential_performance(self, analyzer):
        """Test that parallel execution is faster than sequential"""
        conversation = "Test conversation for performance comparison"
        
        # Test parallel execution (current implementation)
        start_time = time.time()
        await analyzer.analyze(conversation)
        parallel_time = time.time() - start_time
        
        # Test sequential execution by calling functions one by one
        start_time = time.time()
        cleaned_text = analyzer._preprocess_text(conversation)
        await analyzer.extract_topics(cleaned_text)
        await analyzer.identify_planning_elements(cleaned_text)
        await analyzer.detect_user_preferences(cleaned_text)
        await analyzer.extract_action_items(cleaned_text)
        await analyzer.extract_structure(cleaned_text)
        sequential_time = time.time() - start_time
        
        # Parallel should be faster or at least not significantly slower
        # Allow some variance for test environment
        assert parallel_time <= sequential_time * 1.1  # At most 10% slower
        
        print(f"Parallel execution time: {parallel_time:.4f}s")
        print(f"Sequential execution time: {sequential_time:.4f}s")
        print(f"Performance improvement: {((sequential_time - parallel_time) / sequential_time * 100):.1f}%")
    
    @pytest.mark.asyncio
    async def test_large_conversation_handling(self, analyzer):
        """Test analyzer performance with large conversation input"""
        # Create a large conversation (simulating very long chat)
        large_conversation = """
        This is a very long conversation about creating a comprehensive business system.
        """ * 1000  # Repeat to make it large
        
        start_time = time.time()
        result = await analyzer.analyze(large_conversation)
        execution_time = time.time() - start_time
        
        # Should still complete in reasonable time
        assert execution_time < 30  # Should complete within 30 seconds even with large input
        assert isinstance(result, dict)
        assert "topics" in result
    
    @pytest.mark.asyncio
    async def test_concurrent_analyses(self, analyzer):
        """Test running multiple analyses concurrently"""
        conversations = [
            "First conversation about project management",
            "Second conversation about creative workflow",
            "Third conversation about business analytics"
        ]
        
        start_time = time.time()
        
        # Run multiple analyses concurrently
        tasks = [analyzer.analyze(conv) for conv in conversations]
        results = await asyncio.gather(*tasks)
        
        execution_time = time.time() - start_time
        
        # Should handle concurrent requests efficiently
        assert len(results) == 3
        assert all(isinstance(result, dict) for result in results)
        assert execution_time < 20  # Should complete within 20 seconds
        
        print(f"Concurrent analysis time for 3 conversations: {execution_time:.4f}s")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])