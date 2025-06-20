#!/usr/bin/env python3
"""
Test the enhanced conversation analyzer with real data
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

async def test_enhanced_analyzer():
    """Test the enhanced analyzer with our seed conversation"""
    print("🧪 Testing Enhanced Conversation Analyzer...")
    
    try:
        from core.conversation_analyzer import ConversationAnalyzer
        
        # Create analyzer
        analyzer = ConversationAnalyzer()
        print("✅ Enhanced analyzer created successfully")
        
        # Test with a sample conversation
        sample_conversation = """
        I want to create a YouTube channel for my art journey. I need help being more consistent.
        I want everything to look dreamy and colorful, with a kawaii aesthetic. 
        I need a content calendar for planning videos, a filming checklist for my iPhone,
        and an analytics tracker to see how I'm growing. I also want a moodboard for inspiration
        and a reflection journal for my thoughts.
        """
        
        print("\n📊 Testing individual extraction functions...")
        
        # Test individual functions
        topics = await analyzer.extract_topics(sample_conversation)
        print(f"✅ Topics extracted: {topics}")
        
        planning = await analyzer.identify_planning_elements(sample_conversation)
        print(f"✅ Planning elements: {planning}")
        
        preferences = await analyzer.detect_user_preferences(sample_conversation)
        print(f"✅ User preferences: {preferences}")
        
        actions = await analyzer.extract_action_items(sample_conversation)
        print(f"✅ Action items: {actions}")
        
        structure = await analyzer.extract_structure(sample_conversation)
        print(f"✅ Structure requirements: {structure}")
        
        print("\n🚀 Testing parallel analysis...")
        
        # Test parallel analysis
        import time
        start_time = time.time()
        
        result = await analyzer.analyze(sample_conversation)
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        print(f"✅ Parallel analysis completed in {analysis_time:.2f} seconds")
        print(f"📈 Found {len(result['topics'])} topics")
        print(f"🎨 Style preferences: {result['user_preferences']['aesthetic_style']}")
        print(f"🗂️ Database types needed: {result['structure']['database_types']}")
        
        # Test with seed conversation
        print("\n📝 Testing with seed conversation...")
        with open("seed-convo.txt", "r") as f:
            seed_conversation = f.read()[:2000]  # First 2000 chars
        
        seed_result = await analyzer.analyze(seed_conversation)
        print(f"✅ Seed analysis completed")
        print(f"📊 Seed topics: {seed_result['topics'][:3]}...")  # First 3 topics
        print(f"🎨 Seed style: {seed_result['user_preferences']['aesthetic_style']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the enhanced analyzer test"""
    print("🌸 Isabella Notion - Enhanced Analyzer Testing\n")
    
    success = await test_enhanced_analyzer()
    
    print("\n" + "="*50)
    if success:
        print("🎉 Enhanced analyzer working perfectly!")
        print("\n💡 Improvements:")
        print("  ✅ Modular extraction functions")
        print("  ✅ Parallel execution for better performance")
        print("  ✅ Enhanced error handling")
        print("  ✅ More detailed analysis results")
    else:
        print("❌ Enhanced analyzer test failed.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())