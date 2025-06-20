"""
Conversation Analysis Engine
Processes conversations to extract structure, topics, and user preferences
"""

import asyncio
from typing import Dict, List, Any
from openai import AsyncOpenAI
from loguru import logger
import json
import re
from .config import Settings

class ConversationAnalyzer:
    """Analyzes conversations using OpenAI to extract structured information"""
    
    def __init__(self):
        self.settings = Settings()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
    
    async def analyze(self, conversation_text: str) -> Dict[str, Any]:
        """
        Main analysis method that extracts all relevant information from conversation
        
        Args:
            conversation_text: Raw conversation text to analyze
            
        Returns:
            Dict containing topics, planning_elements, user_preferences, action_items, structure
        """
        try:
            # Preprocess the conversation
            cleaned_text = self._preprocess_text(conversation_text)
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(cleaned_text)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing conversations and extracting structured planning information for creating digital workspace templates."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.settings.OPENAI_MAX_TOKENS,
                temperature=self.settings.OPENAI_TEMPERATURE
            )
            
            # Parse the response
            analysis_result = self._parse_analysis_response(response.choices[0].message.content)
            
            logger.info(f"Successfully analyzed conversation with {len(analysis_result.get('topics', []))} topics")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing conversation: {str(e)}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize the conversation text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', text)
        
        # Normalize line breaks
        text = text.replace('\n\n', '\n').replace('\r', '')
        
        return text.strip()
    
    def _build_analysis_prompt(self, conversation_text: str) -> str:
        """Build the analysis prompt for the LLM"""
        return f"""
        Analyze the following conversation and extract structured information for creating a Notion workspace template. 
        
        Return your analysis as a JSON object with these exact keys:
        
        {{
            "topics": ["list of main topics discussed"],
            "planning_elements": {{
                "schedules": ["any scheduling or calendar items mentioned"],
                "checklists": ["any checklist or task items mentioned"],
                "trackers": ["any tracking or monitoring items mentioned"],
                "workflows": ["any workflow or process descriptions"]
            }},
            "user_preferences": {{
                "aesthetic_style": ["style preferences like 'dreamy', 'colorful', 'minimal', etc."],
                "colors": ["specific colors mentioned"],
                "organization_style": ["how they prefer to organize things"],
                "features_requested": ["specific features or functionality requested"]
            }},
            "action_items": ["concrete action items or tasks mentioned"],
            "structure": {{
                "main_categories": ["main organizational categories needed"],
                "database_types": ["types of databases needed like 'content calendar', 'task tracker', etc."],
                "view_types": ["types of views needed like 'calendar', 'kanban', 'gallery', etc."],
                "page_types": ["types of pages needed like 'dashboard', 'templates', 'archives', etc."]
            }}
        }}
        
        Conversation to analyze:
        {conversation_text}
        
        IMPORTANT: Return ONLY the JSON object, no additional text or explanation.
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data"""
        try:
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                json_str = response_text
            
            # Parse JSON
            analysis = json.loads(json_str)
            
            # Validate structure and provide defaults
            default_structure = {
                "topics": [],
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
                    "main_categories": [],
                    "database_types": [],
                    "view_types": [],
                    "page_types": []
                }
            }
            
            # Merge with defaults to ensure all keys exist
            for key, default_value in default_structure.items():
                if key not in analysis:
                    analysis[key] = default_value
                elif isinstance(default_value, dict):
                    for subkey, subdefault in default_value.items():
                        if subkey not in analysis[key]:
                            analysis[key][subkey] = subdefault
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"Response text: {response_text}")
            
            # Return minimal structure if parsing fails
            return {
                "topics": ["General Planning"],
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
                    "main_categories": ["Planning"],
                    "database_types": ["task_tracker"],
                    "view_types": ["table", "calendar"],
                    "page_types": ["dashboard"]
                }
            }