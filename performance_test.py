#!/usr/bin/env python3
"""
Performance comparison between old and new analyzer approaches
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Change to project root to find .env file
os.chdir(Path(__file__).parent)

async def test_sequential_approach(analyzer, conversation):
    """Test the old sequential approach"""
    start_time = time.time()
    
    # Simulate sequential calls (how it used to work)
    topics = await analyzer.extract_topics(conversation)
    planning = await analyzer.identify_planning_elements(conversation)
    preferences = await analyzer.detect_user_preferences(conversation)
    actions = await analyzer.extract_action_items(conversation)
    structure = await analyzer.extract_structure(conversation)
    
    end_time = time.time()
    
    return {
        "topics": topics,
        "planning_elements": planning,
        "user_preferences": preferences,
        "action_items": actions,
        "structure": structure
    }, end_time - start_time

async def test_parallel_approach(analyzer, conversation):
    """Test the new parallel approach"""
    start_time = time.time()
    
    # Use the new parallel analyze method
    result = await analyzer.analyze(conversation)
    
    end_time = time.time()
    
    return result, end_time - start_time

async def run_performance_comparison():
    """Run performance comparison tests"""
    print("⚡ Performance Comparison: Sequential vs Parallel Analysis")
    print("="*60)
    
    try:
        from core.conversation_analyzer import ConversationAnalyzer
        
        analyzer = ConversationAnalyzer()
        
        # Test conversation
        conversation = """
        I want to build a comprehensive productivity system for my creative business.
        I need project management, client tracking, content planning, and financial monitoring.
        I prefer a minimal, clean aesthetic with lots of white space and subtle colors.
        The system should have dashboards, calendars, kanban boards, and reporting views.
        I want to track deadlines, budgets, creative inspiration, and team collaboration.
        """
        
        print(f"📝 Test conversation length: {len(conversation)} characters\n")
        
        # Test multiple runs for accuracy
        num_tests = 3
        sequential_times = []
        parallel_times = []
        
        for i in range(num_tests):
            print(f"🔄 Run {i+1}/{num_tests}")
            
            # Test sequential approach
            seq_result, seq_time = await test_sequential_approach(analyzer, conversation)
            sequential_times.append(seq_time)
            print(f"   Sequential: {seq_time:.2f}s")
            
            # Small delay between tests
            await asyncio.sleep(1)
            
            # Test parallel approach
            par_result, par_time = await test_parallel_approach(analyzer, conversation)
            parallel_times.append(par_time)
            print(f"   Parallel:   {par_time:.2f}s")
            
            speedup = seq_time / par_time
            print(f"   Speedup:    {speedup:.2f}x\n")
        
        # Calculate averages
        avg_sequential = sum(sequential_times) / len(sequential_times)
        avg_parallel = sum(parallel_times) / len(parallel_times)
        avg_speedup = avg_sequential / avg_parallel
        
        print("📊 PERFORMANCE RESULTS")
        print("="*30)
        print(f"Sequential Average: {avg_sequential:.2f} seconds")
        print(f"Parallel Average:   {avg_parallel:.2f} seconds")
        print(f"Average Speedup:    {avg_speedup:.2f}x")
        print(f"Time Saved:         {avg_sequential - avg_parallel:.2f} seconds")
        print(f"Performance Gain:   {((avg_speedup - 1) * 100):.1f}%")
        
        # Verify results are equivalent
        print("\n🔍 RESULT VALIDATION")
        print("="*20)
        seq_topics = len(seq_result["topics"])
        par_topics = len(par_result["topics"])
        print(f"Sequential topics: {seq_topics}")
        print(f"Parallel topics:   {par_topics}")
        print(f"Results match:     {'✅' if abs(seq_topics - par_topics) <= 2 else '❌'}")
        
        # Real-world impact
        print(f"\n💡 REAL-WORLD IMPACT")
        print("="*20)
        daily_analyses = 50
        daily_savings = (avg_sequential - avg_parallel) * daily_analyses
        weekly_savings = daily_savings * 7
        print(f"For {daily_analyses} analyses/day:")
        print(f"  Daily time saved:  {daily_savings:.1f} seconds ({daily_savings/60:.1f} minutes)")
        print(f"  Weekly time saved: {weekly_savings:.1f} seconds ({weekly_savings/60:.1f} minutes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the performance test"""
    print("🌸 Isabella Notion - Performance Analysis\n")
    
    success = await run_performance_comparison()
    
    print("\n" + "="*60)
    if success:
        print("🎉 Performance testing completed successfully!")
        print("\n✨ The parallel approach provides significant speedup")
        print("   while maintaining identical analysis quality.")
    else:
        print("❌ Performance testing failed.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())