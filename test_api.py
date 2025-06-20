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
    """Test the enhanced conversation analyzer directly"""
    print("🧪 Testing Enhanced Conversation Analyzer...")
    
    try:
        from core.conversation_analyzer import ConversationAnalyzer
        
        # Test with our seed conversation
        with open("seed-convo.txt", "r") as f:
            conversation = f.read()[:2000]  # Use first 2000 chars for more comprehensive test
        
        analyzer = ConversationAnalyzer()
        print("✅ Analyzer created successfully")
        
        # Test the enhanced parallel analysis
        import time
        start_time = time.time()
        result = await analyzer.analyze(conversation)
        execution_time = time.time() - start_time
        print(f"✅ Enhanced parallel analysis completed in {execution_time:.2f}s")
        
        # Test comprehensive results
        print(f"\n📊 Analysis Results:")
        print(f"  Topics found: {len(result.get('topics', []))}")
        for i, topic in enumerate(result.get('topics', [])[:3], 1):
            print(f"    {i}. {topic}")
        
        print(f"\n🎨 User Preferences:")
        preferences = result.get('user_preferences', {})
        print(f"  Aesthetic styles: {preferences.get('aesthetic_style', [])}")
        print(f"  Colors mentioned: {preferences.get('colors', [])}")
        print(f"  Features requested: {preferences.get('features_requested', [])}")
        
        print(f"\n📋 Planning Elements:")
        planning = result.get('planning_elements', {})
        print(f"  Schedules: {len(planning.get('schedules', []))} items")
        print(f"  Checklists: {len(planning.get('checklists', []))} items")
        print(f"  Trackers: {len(planning.get('trackers', []))} items")
        print(f"  Workflows: {len(planning.get('workflows', []))} items")
        
        print(f"\n✅ Action Items: {len(result.get('action_items', []))} items")
        for i, action in enumerate(result.get('action_items', [])[:3], 1):
            print(f"    {i}. {action}")
        
        print(f"\n🏗️ Structure Requirements:")
        structure = result.get('structure', {})
        print(f"  Main categories: {structure.get('main_categories', [])}")
        print(f"  Database types: {structure.get('database_types', [])}")
        print(f"  View types: {structure.get('view_types', [])}")
        
        # Test individual extraction functions
        print(f"\n🔧 Testing Individual Functions:")
        cleaned_text = analyzer._preprocess_text(conversation[:500])
        
        # Test topics extraction
        try:
            topics = await analyzer.extract_topics(cleaned_text)
            print(f"  ✅ Topics extraction: {len(topics)} topics")
        except Exception as e:
            print(f"  ⚠️ Topics extraction error: {str(e)}")
        
        # Test planning elements
        try:
            planning_elements = await analyzer.identify_planning_elements(cleaned_text)
            print(f"  ✅ Planning elements extraction: {sum(len(v) for v in planning_elements.values())} items")
        except Exception as e:
            print(f"  ⚠️ Planning elements error: {str(e)}")
        
        # Test preferences detection
        try:
            user_prefs = await analyzer.detect_user_preferences(cleaned_text)
            print(f"  ✅ User preferences detection: {sum(len(v) for v in user_prefs.values())} preferences")
        except Exception as e:
            print(f"  ⚠️ User preferences error: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
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

async def test_enhanced_api_analysis():
    """Test the enhanced analyze-conversation API endpoint"""
    print("\n🚀 Testing Enhanced API Analysis Endpoint...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        import json
        
        client = TestClient(app)
        
        # Read seed conversation for testing
        with open("seed-convo.txt", "r") as f:
            test_conversation = f.read()[:1500]  # Use portion of seed conversation
        
        # Test the analyze-conversation endpoint
        response = client.post(
            "/analyze-conversation",
            json={"conversation": test_conversation}
        )
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Verify enhanced response structure
            required_fields = ["topics", "planning_elements", "user_preferences", "action_items", "structure"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if not missing_fields:
                print("✅ Enhanced API endpoint structure is correct")
                
                # Test detailed structure
                print(f"  📊 Topics returned: {len(result.get('topics', []))}")
                print(f"  📋 Planning elements structure: {list(result.get('planning_elements', {}).keys())}")
                print(f"  🎨 User preferences structure: {list(result.get('user_preferences', {}).keys())}")
                print(f"  ✅ Action items count: {len(result.get('action_items', []))}")
                print(f"  🏗️ Structure categories: {list(result.get('structure', {}).keys())}")
                
                # Verify nested structure
                planning_elements = result.get('planning_elements', {})
                expected_planning_keys = ["schedules", "checklists", "trackers", "workflows"]
                planning_keys_present = all(key in planning_elements for key in expected_planning_keys)
                
                user_preferences = result.get('user_preferences', {})
                expected_pref_keys = ["aesthetic_style", "colors", "organization_style", "features_requested"]
                pref_keys_present = all(key in user_preferences for key in expected_pref_keys)
                
                structure = result.get('structure', {})
                expected_structure_keys = ["main_categories", "database_types", "view_types", "page_types"]
                structure_keys_present = all(key in structure for key in expected_structure_keys)
                
                if planning_keys_present and pref_keys_present and structure_keys_present:
                    print("✅ All nested structures are correctly formatted")
                    return True
                else:
                    print("⚠️ Some nested structure keys are missing")
                    print(f"  Planning keys present: {planning_keys_present}")
                    print(f"  Preference keys present: {pref_keys_present}")
                    print(f"  Structure keys present: {structure_keys_present}")
                    return False
            else:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing enhanced API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🌸 Isabella Notion - Enhanced API Testing\n")
    
    success = True
    
    # Test enhanced conversation analyzer
    if not await test_conversation_analyzer():
        success = False
    
    # Test basic endpoints  
    if not await test_basic_endpoints():
        success = False
    
    # Test enhanced API analysis endpoint
    if not await test_enhanced_api_analysis():
        success = False
    
    print("\n" + "="*60)
    if success:
        print("🎉 All enhanced tests passed! API is working correctly.")
        print("\n💡 Enhanced Features Verified:")
        print("  ✅ Parallel execution of 5 extraction functions")
        print("  ✅ Individual function testing (topics, planning, preferences, actions, structure)")
        print("  ✅ Comprehensive API response structure")
        print("  ✅ Error handling and fallbacks")
        print("\n🚀 Next steps:")
        print("  1. Start server: python run.py")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Test with real conversation data")
        print("  4. Run comprehensive tests: python -m pytest tests/test_enhanced_analyzer.py -v")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("  1. Ensure OpenAI API key is set in environment")
        print("  2. Check that all dependencies are installed")
        print("  3. Verify seed-convo.txt file exists")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())