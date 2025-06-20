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
            
            # Run all extraction functions in parallel for better performance
            tasks = [
                self.extract_topics(cleaned_text),
                self.identify_planning_elements(cleaned_text),
                self.detect_user_preferences(cleaned_text),
                self.extract_action_items(cleaned_text),
                self.extract_structure(cleaned_text)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Combine results
            analysis_result = {
                "topics": results[0],
                "planning_elements": results[1],
                "user_preferences": results[2],
                "action_items": results[3],
                "structure": results[4]
            }
            
            logger.info(f"Successfully analyzed conversation with {len(analysis_result.get('topics', []))} topics")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing conversation: {str(e)}")
            raise
    
    async def extract_topics(self, conversation_text: str) -> List[str]:
        """Extract main topics and categories from conversation"""
        prompt = f"""
        Analyze this conversation and extract the main topics being discussed.
        Return only a JSON array of topic strings, maximum 10 topics.
        
        Conversation: {conversation_text}
        
        Return format: ["topic1", "topic2", "topic3"]
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying conversation topics. Return only JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return result if isinstance(result, list) else []
            
        except Exception as e:
            logger.warning(f"Error extracting topics: {str(e)}")
            return ["General Planning"]
    
    async def identify_planning_elements(self, conversation_text: str) -> Dict[str, List[str]]:
        """Extract schedules, checklists, trackers, and workflows"""
        prompt = f"""
        Analyze this conversation and extract planning elements.
        Return only a JSON object with these exact keys:
        
        {{
            "schedules": ["schedule items mentioned"],
            "checklists": ["checklist items mentioned"],
            "trackers": ["tracking items mentioned"],
            "workflows": ["workflow descriptions mentioned"]
        }}
        
        Conversation: {conversation_text}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying planning elements in conversations. Return only JSON objects."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "schedules": result.get("schedules", []),
                "checklists": result.get("checklists", []),
                "trackers": result.get("trackers", []),
                "workflows": result.get("workflows", [])
            }
            
        except Exception as e:
            logger.warning(f"Error identifying planning elements: {str(e)}")
            return {"schedules": [], "checklists": [], "trackers": [], "workflows": []}
    
    async def detect_user_preferences(self, conversation_text: str) -> Dict[str, List[str]]:
        """Parse style preferences, colors, organization style, and features"""
        prompt = f"""
        Analyze this conversation and extract user preferences.
        Return only a JSON object with these exact keys:
        
        {{
            "aesthetic_style": ["style words like 'dreamy', 'colorful', 'minimal', etc."],
            "colors": ["specific colors mentioned"],
            "organization_style": ["how they prefer to organize"],
            "features_requested": ["specific features they want"]
        }}
        
        Conversation: {conversation_text}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying user preferences and style choices. Return only JSON objects."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "aesthetic_style": result.get("aesthetic_style", []),
                "colors": result.get("colors", []),
                "organization_style": result.get("organization_style", []),
                "features_requested": result.get("features_requested", [])
            }
            
        except Exception as e:
            logger.warning(f"Error detecting user preferences: {str(e)}")
            return {"aesthetic_style": [], "colors": [], "organization_style": [], "features_requested": []}
    
    async def extract_action_items(self, conversation_text: str) -> List[str]:
        """Identify concrete tasks and action items"""
        prompt = f"""
        Analyze this conversation and extract concrete action items or tasks mentioned.
        Return only a JSON array of action item strings.
        
        Conversation: {conversation_text}
        
        Return format: ["action1", "action2", "action3"]
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying actionable tasks from conversations. Return only JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return result if isinstance(result, list) else []
            
        except Exception as e:
            logger.warning(f"Error extracting action items: {str(e)}")
            return []
    
    async def extract_structure(self, conversation_text: str) -> Dict[str, List[str]]:
        """Extract organizational structure requirements"""
        prompt = f"""
        Analyze this conversation and determine what organizational structure they need.
        Return only a JSON object with these exact keys:
        
        {{
            "main_categories": ["main organizational categories needed"],
            "database_types": ["types of databases like 'content_calendar', 'task_tracker', etc."],
            "view_types": ["types of views like 'calendar', 'kanban', 'gallery', etc."],
            "page_types": ["types of pages like 'dashboard', 'templates', 'archives', etc."]
        }}
        
        Conversation: {conversation_text}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at determining organizational structure needs. Return only JSON objects."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=700,
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "main_categories": result.get("main_categories", []),
                "database_types": result.get("database_types", []),
                "view_types": result.get("view_types", []),
                "page_types": result.get("page_types", [])
            }
            
        except Exception as e:
            logger.warning(f"Error extracting structure: {str(e)}")
            return {
                "main_categories": ["Planning"],
                "database_types": ["task_tracker"],
                "view_types": ["table", "calendar"],
                "page_types": ["dashboard"]
            }
    
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