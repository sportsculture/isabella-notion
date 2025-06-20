"""
Notion Template Generator
Creates Notion templates based on conversation analysis
"""

from typing import Dict, List, Any, Optional
from notion_client import AsyncClient
from loguru import logger
import asyncio
from datetime import datetime
import uuid

class NotionGenerator:
    """Generates Notion templates from conversation analysis"""
    
    def __init__(self, notion_api_key: str):
        self.client = AsyncClient(auth=notion_api_key)
        self.notion_version = "2022-06-28"
    
    async def create_template(
        self, 
        analysis: Dict[str, Any], 
        style_preferences: Optional[Dict[str, Any]] = None,
        template_name: str = "Generated Template"
    ) -> Dict[str, str]:
        """
        Create a complete Notion template based on conversation analysis
        
        Args:
            analysis: Analysis results from ConversationAnalyzer
            style_preferences: Optional style preferences to override analysis
            template_name: Name for the template
            
        Returns:
            Dict with template_url and template_id
        """
        try:
            # Create main template page
            main_page = await self._create_main_page(template_name, analysis)
            
            # Create databases based on analysis
            databases = await self._create_databases(main_page["id"], analysis)
            
            # Create additional pages
            pages = await self._create_additional_pages(main_page["id"], analysis)
            
            # Apply styling based on preferences
            await self._apply_styling(main_page["id"], analysis, style_preferences)
            
            # Get shareable URL
            template_url = await self._get_shareable_url(main_page["id"])
            
            logger.info(f"Successfully created Notion template: {template_name}")
            
            return {
                "template_url": template_url,
                "template_id": main_page["id"],
                "databases": databases,
                "pages": pages
            }
            
        except Exception as e:
            logger.error(f"Error creating Notion template: {str(e)}")
            raise
    
    async def _create_main_page(self, template_name: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create the main template page"""
        
        # Extract key information for page content
        topics = analysis.get("topics", [])
        main_categories = analysis.get("structure", {}).get("main_categories", [])
        
        # Build page content
        children = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": template_name}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"Generated on {datetime.now().strftime('%B %d, %Y')}"}
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📋 Overview"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"This template covers: {', '.join(topics[:5]) if topics else 'General planning and organization'}"}
                        }
                    ]
                }
            }
        ]
        
        # Add main categories section if available
        if main_categories:
            children.append({
                "object": "block",
                "type": "heading_2", 
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "🗂️ Main Categories"}}]
                }
            })
            
            # Add category list items
            for category in main_categories[:10]:  # Limit to 10 categories
                children.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {"type": "text", "text": {"content": category}}
                        ]
                    }
                })
        
        response = await self.client.pages.create(
            parent={"type": "page_id", "page_id": await self._get_workspace_id()},
            properties={
                "title": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": template_name}
                        }
                    ]
                }
            },
            children=children
        )
        
        return response
    
    async def _create_databases(self, parent_page_id: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create databases based on analysis"""
        databases = []
        database_types = analysis.get("structure", {}).get("database_types", [])
        
        # Create different types of databases based on analysis
        for db_type in database_types:
            if "content" in db_type.lower() or "calendar" in db_type.lower():
                db = await self._create_content_database(parent_page_id, analysis)
                databases.append(db)
            elif "task" in db_type.lower() or "todo" in db_type.lower():
                db = await self._create_task_database(parent_page_id, analysis)
                databases.append(db)
            elif "tracker" in db_type.lower() or "analytics" in db_type.lower():
                db = await self._create_tracker_database(parent_page_id, analysis)
                databases.append(db)
        
        # If no specific database types identified, create a general planning database
        if not databases:
            db = await self._create_general_database(parent_page_id, analysis)
            databases.append(db)
        
        return databases
    
    async def _create_content_database(self, parent_page_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a content planning database"""
        return await self.client.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "📅 Content Calendar"}}],
            properties={
                "Name": {"title": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Idea", "color": "yellow"},
                            {"name": "Planned", "color": "blue"},
                            {"name": "In Progress", "color": "orange"},
                            {"name": "Complete", "color": "green"}
                        ]
                    }
                },
                "Date": {"date": {}},
                "Type": {
                    "select": {
                        "options": [
                            {"name": "Video", "color": "red"},
                            {"name": "Post", "color": "blue"},
                            {"name": "Article", "color": "green"}
                        ]
                    }
                },
                "Priority": {
                    "select": {
                        "options": [
                            {"name": "High", "color": "red"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "Low", "color": "gray"}
                        ]
                    }
                }
            }
        )
    
    async def _create_task_database(self, parent_page_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task tracking database"""
        return await self.client.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "✅ Task Tracker"}}],
            properties={
                "Task": {"title": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Not Started", "color": "default"},
                            {"name": "In Progress", "color": "blue"},
                            {"name": "Completed", "color": "green"},
                            {"name": "Blocked", "color": "red"}
                        ]
                    }
                },
                "Due Date": {"date": {}},
                "Priority": {
                    "select": {
                        "options": [
                            {"name": "High", "color": "red"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "Low", "color": "gray"}
                        ]
                    }
                },
                "Category": {"multi_select": {"options": []}}
            }
        )
    
    async def _create_tracker_database(self, parent_page_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a tracker/analytics database"""
        return await self.client.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "📊 Analytics Tracker"}}],
            properties={
                "Item": {"title": {}},
                "Date": {"date": {}},
                "Value": {"number": {}},
                "Notes": {"rich_text": {}},
                "Category": {
                    "select": {
                        "options": [
                            {"name": "Views", "color": "blue"},
                            {"name": "Engagement", "color": "green"},
                            {"name": "Growth", "color": "purple"}
                        ]
                    }
                }
            }
        )
    
    async def _create_general_database(self, parent_page_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a general planning database"""
        return await self.client.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "📋 Planning Board"}}],
            properties={
                "Name": {"title": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Idea", "color": "yellow"},
                            {"name": "Planning", "color": "blue"},
                            {"name": "In Progress", "color": "orange"},
                            {"name": "Done", "color": "green"}
                        ]
                    }
                },
                "Date": {"date": {}},
                "Priority": {
                    "select": {
                        "options": [
                            {"name": "High", "color": "red"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "Low", "color": "gray"}
                        ]
                    }
                },
                "Notes": {"rich_text": {}}
            }
        )
    
    async def _create_additional_pages(self, parent_page_id: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create additional pages based on analysis"""
        pages = []
        page_types = analysis.get("structure", {}).get("page_types", [])
        
        # Create common pages
        if "moodboard" in str(page_types).lower() or "inspiration" in str(analysis).lower():
            pages.append(await self._create_moodboard_page(parent_page_id))
        
        if "reflection" in str(page_types).lower() or "journal" in str(analysis).lower():
            pages.append(await self._create_reflection_page(parent_page_id))
        
        if "checklist" in str(analysis).lower():
            pages.append(await self._create_checklist_page(parent_page_id, analysis))
        
        return pages
    
    async def _create_moodboard_page(self, parent_page_id: str) -> Dict[str, Any]:
        """Create a moodboard/inspiration page"""
        return await self.client.pages.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            properties={
                "title": {
                    "title": [{"type": "text", "text": {"content": "🎨 Moodboard & Inspiration"}}]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "Visual Inspiration"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Drag and drop images, colors, and inspiration here."}}
                        ]
                    }
                }
            ]
        )
    
    async def _create_reflection_page(self, parent_page_id: str) -> Dict[str, Any]:
        """Create a reflection/journal page"""
        return await self.client.pages.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            properties={
                "title": {
                    "title": [{"type": "text", "text": {"content": "💭 Reflection Journal"}}]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "Weekly Reflections"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Use this space for weekly reflection prompts and thoughts."}}
                        ]
                    }
                }
            ]
        )
    
    async def _create_checklist_page(self, parent_page_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a checklist page with items from analysis"""
        checklists = analysis.get("planning_elements", {}).get("checklists", [])
        
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Checklist Items"}}]
                }
            }
        ]
        
        # Add checklist items from analysis
        for item in checklists[:10]:  # Limit to 10 items
            children.append({
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": item}}],
                    "checked": False
                }
            })
        
        return await self.client.pages.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            properties={
                "title": {
                    "title": [{"type": "text", "text": {"content": "✅ Checklists"}}]
                }
            },
            children=children
        )
    
    async def _apply_styling(
        self, 
        page_id: str, 
        analysis: Dict[str, Any], 
        style_preferences: Optional[Dict[str, Any]]
    ):
        """Apply styling based on preferences (placeholder for future enhancement)"""
        # Note: Notion API has limited styling options
        # This is a placeholder for future styling enhancements
        pass
    
    async def _get_shareable_url(self, page_id: str) -> str:
        """Get shareable URL for the template"""
        # For now, return the standard Notion URL format
        # In a real implementation, you might want to make the page public
        return f"https://notion.so/{page_id.replace('-', '')}"
    
    async def _get_workspace_id(self) -> str:
        """Get the workspace ID for creating pages"""
        # This is a simplified implementation
        # In reality, you'd need to handle workspace detection properly
        # For now, we'll use the user's default workspace
        # You might need to list pages and use one as parent, or handle this differently
        
        # List the user's pages to find a suitable parent
        try:
            search_results = await self.client.search()
            if search_results.get("results"):
                # Use the first page as parent (simplified approach)
                return search_results["results"][0]["id"]
            else:
                # If no pages found, you'll need to handle this case
                # This might require creating a new page in the root workspace
                raise Exception("No pages found in workspace. Please create at least one page in your Notion workspace first.")
        except Exception as e:
            logger.error(f"Error getting workspace ID: {str(e)}")
            raise Exception("Unable to access Notion workspace. Please check your API key and permissions.")