# 🌸 Isabella Notion

**AI-Powered Conversation to Notion Template Generator**

Transform your planning conversations into beautiful, functional Notion workspaces automatically.

## ✨ What It Does

Isabella Notion analyzes your conversations about planning, organizing, or structuring content and automatically generates customized Notion templates with:

- 📅 **Content Calendars** - Organized scheduling systems
- ✅ **Task Trackers** - Kanban boards and to-do lists  
- 📊 **Analytics Dashboards** - Performance tracking
- 🎨 **Moodboards** - Visual inspiration galleries
- 💭 **Reflection Journals** - Prompted writing spaces
- 🌈 **Custom Styling** - Aesthetic preferences applied

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Notion API key

### Installation

1. **Clone and setup**
```bash
git clone <repo-url>
cd isabella-notion
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run the application**
```bash
cd src
python main.py
```

The API will be available at `http://localhost:8000`

### 📚 API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## 🔥 Example Usage

### Analyze a Conversation
```bash
curl -X POST "http://localhost:8000/analyze-conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": "I want to plan my YouTube channel better. I need a content calendar, filming checklist, and want everything to look dreamy and colorful."
  }'
```

### Generate a Template
```bash
curl -X POST "http://localhost:8000/generate-template" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": "Your planning conversation here...",
    "notion_api_key": "your_notion_key",
    "template_name": "My YouTube Planner"
  }'
```

## 🏗️ Architecture

```
src/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── config.py          # Configuration management
│   ├── conversation_analyzer.py  # AI conversation processing
│   └── notion_generator.py       # Notion template creation
├── templates/             # Template definitions
└── tests/                # Test suite
```

## 🧪 Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black src/
isort src/
flake8 src/
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for conversation analysis | ✅ |
| `NOTION_API_KEY` | Notion API key (can be per-request) | ⚠️ |
| `APP_HOST` | Application host (default: localhost) | ❌ |
| `APP_PORT` | Application port (default: 8000) | ❌ |
| `DEBUG` | Debug mode (default: true) | ❌ |

## 📋 Project Status

This project was generated using [Task Master AI](https://github.com/eyaltoledano/taskmaster-ai) from a comprehensive PRD.

**Current Progress:**
- ✅ Project setup and configuration
- 🚧 Conversation analysis engine (in development)
- ⏳ Template generation system
- ⏳ Notion API integration
- ⏳ Aesthetic customization
- ⏳ API interface
- ⏳ Comprehensive testing

## 🤝 Contributing

This is a personal project, but suggestions and ideas are welcome! Please open an issue to discuss potential changes.

## 📄 License

MIT License - see LICENSE file for details.

---

*Built with ❤️ using Python, FastAPI, OpenAI, and Notion APIs*