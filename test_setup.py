#!/usr/bin/env python3
"""
Setup validation script for Isabella Notion
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all core modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from core.config import Settings, validate_environment
        print("  ✅ Config module imported")
    except ImportError as e:
        print(f"  ❌ Config import failed: {e}")
        return False
    
    try:
        from core.conversation_analyzer import ConversationAnalyzer
        print("  ✅ Conversation analyzer imported")
    except ImportError as e:
        print(f"  ❌ Conversation analyzer import failed: {e}")
        return False
    
    try:
        from core.notion_generator import NotionGenerator
        print("  ✅ Notion generator imported")
    except ImportError as e:
        print(f"  ❌ Notion generator import failed: {e}")
        return False
    
    try:
        from main import app
        print("  ✅ Main FastAPI app imported")
    except ImportError as e:
        print(f"  ❌ Main app import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ .env file found")
    else:
        print("  ⚠️  .env file not found (using .env.example as reference)")
    
    # Try to load settings
    try:
        from core.config import Settings
        settings = Settings()
        print(f"  ✅ Settings loaded - Debug: {settings.DEBUG}")
    except Exception as e:
        print(f"  ❌ Settings loading failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality without API calls"""
    print("\n🔍 Testing basic functionality...")
    
    try:
        from core.conversation_analyzer import ConversationAnalyzer
        analyzer = ConversationAnalyzer()
        
        # Test text preprocessing
        test_text = "Hello   world!\n\n\nThis  has   extra    spaces."
        cleaned = analyzer._preprocess_text(test_text)
        print(f"  ✅ Text preprocessing works")
        
        # Test prompt building
        prompt = analyzer._build_analysis_prompt("test conversation")
        if "JSON" in prompt and "topics" in prompt:
            print("  ✅ Prompt building works")
        else:
            print("  ❌ Prompt building failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        return False
    
    return True

def main():
    """Run all validation tests"""
    print("🌸 Isabella Notion - Setup Validation\n")
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test environment
    if not test_environment():
        all_passed = False
    
    # Test basic functionality
    if not test_basic_functionality():
        all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All tests passed! Setup looks good.")
        print("\n💡 Next steps:")
        print("  1. Set up your .env file with API keys")
        print("  2. Run: python run.py")
        print("  3. Visit: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n💡 Common fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Create .env file from .env.example")
        print("  3. Check Python path and imports")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)