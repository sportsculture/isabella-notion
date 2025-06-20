# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Isabella Notion** is an AI-powered tool that converts planning conversations into structured Notion templates. Built with Python, FastAPI, OpenAI, and Notion APIs.

## Architecture

- **Framework**: FastAPI (Python 3.8+)
- **AI Processing**: OpenAI GPT-4 for conversation analysis
- **Notion Integration**: Official Notion API client
- **Structure**: Modular core with conversation analysis and template generation

## Development Commands

### Setup & Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application
```bash
# Validate setup
python test_setup.py

# Start development server
python run.py

# Alternative direct start
cd src && python main.py
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Test specific module
pytest tests/test_basic.py -v
```

### Code Quality
```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/

# All quality checks
black src/ && isort src/ && flake8 src/
```

## Key Architecture Components

### Core Modules
- `src/main.py` - FastAPI application with REST endpoints
- `src/core/conversation_analyzer.py` - AI-powered conversation processing
- `src/core/notion_generator.py` - Notion template creation engine
- `src/core/config.py` - Environment and settings management

### API Endpoints
- `POST /analyze-conversation` - Extract structure from conversation text
- `POST /generate-template` - Create full Notion template from conversation
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

### Template Generation Process
1. **Conversation Analysis** - Extract topics, preferences, structure using GPT-4
2. **Template Mapping** - Map analysis to Notion components (databases, pages, views)
3. **Notion Creation** - Use Notion API to create pages, databases, and content
4. **Styling Application** - Apply aesthetic preferences from conversation
5. **URL Generation** - Return shareable template link

## Environment Variables

Required:
- `OPENAI_API_KEY` - For conversation analysis
- `NOTION_API_KEY` - For template creation (can be per-request)

Optional:
- `APP_HOST` - Server host (default: localhost)
- `APP_PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: true)
- `OPENAI_MODEL` - AI model (default: gpt-4)

## Task Management

This project uses [Task Master AI](https://github.com/eyaltoledano/taskmaster-ai) for development planning:

```bash
# View current tasks
task-master list

# Show next task to work on
task-master next

# Mark task as in-progress
task-master set-status --id=X --status=in-progress

# Mark task as done
task-master set-status --id=X --status=done
```

## File Structure

```
├── src/
│   ├── main.py                 # FastAPI app entry point
│   └── core/
│       ├── config.py          # Settings management
│       ├── conversation_analyzer.py  # AI processing
│       └── notion_generator.py       # Template creation
├── tests/                     # Test suite
├── .taskmaster/              # Task management files
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── README.md                 # Project documentation
```

## Common Workflows

### Adding New Template Types
1. Extend `ConversationAnalyzer` to detect new patterns
2. Add corresponding database/page creation in `NotionGenerator`
3. Update API models if needed
4. Add tests for new functionality

### Debugging API Issues
1. Check logs in console output
2. Use `/docs` endpoint for API testing
3. Validate environment variables with `test_setup.py`
4. Test individual components with pytest

### Deployment Preparation
1. Set `DEBUG=false` in production
2. Configure proper CORS origins
3. Use production-grade ASGI server (gunicorn + uvicorn)
4. Secure API key handling

## Security Notes

- API keys are loaded from environment variables only
- No API keys stored in code or version control
- Input validation on all endpoints
- Error handling prevents sensitive data leakage