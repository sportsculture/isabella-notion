"""
Isabella Notion - Conversation to Notion Template Generator
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
from loguru import logger

from core.config import Settings
from core.conversation_analyzer import ConversationAnalyzer
from core.notion_generator import NotionGenerator

# Load environment variables
load_dotenv()

# Initialize settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="Isabella Notion",
    description="AI-powered Conversation to Notion Template Generator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class GenerateTemplateRequest(BaseModel):
    conversation: str
    notion_api_key: str
    style_preferences: Optional[Dict[str, Any]] = None
    template_name: Optional[str] = "Generated Template"

class AnalyzeConversationRequest(BaseModel):
    conversation: str

# Response models
class AnalysisResponse(BaseModel):
    topics: list
    planning_elements: dict
    user_preferences: dict
    action_items: list
    structure: dict

class GenerateTemplateResponse(BaseModel):
    template_url: str
    analysis: AnalysisResponse
    template_id: str
    status: str

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Isabella Notion API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Main endpoints
@app.post("/analyze-conversation", response_model=AnalysisResponse)
async def analyze_conversation(request: AnalyzeConversationRequest):
    """
    Analyze a conversation to extract structure, topics, and preferences
    """
    try:
        analyzer = ConversationAnalyzer()
        analysis = await analyzer.analyze(request.conversation)
        
        return AnalysisResponse(
            topics=analysis["topics"],
            planning_elements=analysis["planning_elements"],
            user_preferences=analysis["user_preferences"],
            action_items=analysis["action_items"],
            structure=analysis["structure"]
        )
    except Exception as e:
        logger.error(f"Error analyzing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/generate-template", response_model=GenerateTemplateResponse)
async def generate_template(request: GenerateTemplateRequest):
    """
    Generate a Notion template from a conversation
    """
    try:
        # Step 1: Analyze the conversation
        analyzer = ConversationAnalyzer()
        analysis = await analyzer.analyze(request.conversation)
        
        # Step 2: Generate Notion template
        generator = NotionGenerator(request.notion_api_key)
        template_result = await generator.create_template(
            analysis, 
            request.style_preferences,
            request.template_name
        )
        
        return GenerateTemplateResponse(
            template_url=template_result["template_url"],
            template_id=template_result["template_id"],
            analysis=AnalysisResponse(
                topics=analysis["topics"],
                planning_elements=analysis["planning_elements"],
                user_preferences=analysis["user_preferences"],
                action_items=analysis["action_items"],
                structure=analysis["structure"]
            ),
            status="success"
        )
    except Exception as e:
        logger.error(f"Error generating template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Template generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )