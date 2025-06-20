#!/usr/bin/env python3
"""
Isabella Notion - Startup Script
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main startup function"""
    try:
        # Import and validate configuration
        from core.config import validate_environment
        validate_environment()
        print("✅ Environment validation passed")
        
        # Import the FastAPI app
        from main import app
        print("✅ Application imported successfully")
        
        # Start the server
        import uvicorn
        print("🚀 Starting Isabella Notion API server...")
        print("📚 API docs will be available at: http://localhost:8000/docs")
        
        uvicorn.run(
            "main:app",
            host="localhost",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you've installed dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Check your .env file and ensure API keys are set")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()