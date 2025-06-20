#!/usr/bin/env python3
"""
Quick API test for Isabella Notion
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Change to project root to find .env file
os.chdir(Path(__file__).parent)

async def test_conversation_analyzer():
    """Test the conversation analyzer directly"""
    print("🧪 Testing Conversation Analyzer...")
    
    try:
        from core.conversation_analyzer import ConversationAnalyzer
        
        # Test with our seed conversation
        with open("seed-convo.txt", "r") as f:
            conversation = f.read()[:1000]  # Use first 1000 chars
        
        analyzer = ConversationAnalyzer()
        print("✅ Analyzer created successfully")
        
        # Test the analysis
        result = await analyzer.analyze(conversation)
        print("✅ Analysis completed successfully")
        
        print(f"📊 Found {len(result.get('topics', []))} topics:")
        for topic in result.get('topics', [])[:3]:
            print(f"  - {topic}")
        
        print(f"🎨 Style preferences: {result.get('user_preferences', {}).get('aesthetic_style', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_basic_endpoints():
    """Test basic endpoints without starting full server"""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        print(f"✅ Health endpoint: {response.status_code} - {response.json()}")
        
        # Test root endpoint
        response = client.get("/")
        print(f"✅ Root endpoint: {response.status_code} - {response.json()['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🌸 Isabella Notion - API Testing\n")
    
    success = True
    
    # Test conversation analyzer
    if not await test_conversation_analyzer():
        success = False
    
    # Test basic endpoints  
    if not await test_basic_endpoints():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 All tests passed! API is working correctly.")
        print("\n💡 Next steps:")
        print("  1. Start server: python run.py")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Test with real conversation data")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())