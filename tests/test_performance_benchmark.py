"""
Performance benchmark test for parallel vs sequential execution
Demonstrates the performance improvement of the enhanced analyzer
"""

import asyncio
import time
import statistics
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.conversation_analyzer import ConversationAnalyzer


class PerformanceBenchmark:
    """Benchmark the performance improvements of parallel execution"""
    
    def __init__(self):
        self.sample_conversation = """
        I'm starting a creative business and need help organizing everything. 
        I want a dreamy, colorful workspace with kawaii aesthetics using pastel colors 
        like pink, lavender, and mint green. I need to track my art projects, manage 
        client relationships, schedule content creation, and organize my supplies. 
        I'd like a content calendar for social media, a project tracker with kanban views, 
        a client database, and an inventory system for my art supplies. Can you help me 
        create workflows for my daily routines, weekly planning sessions, and monthly 
        business reviews? I also need templates for project briefs, client contracts, 
        and creative mood boards.
        """
    
    def create_mock_analyzer(self, delay_seconds=0.1):
        """Create analyzer with controlled delay to simulate API calls"""
        with patch('core.conversation_analyzer.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            async def mock_create(*args, **kwargs):
                # Simulate API delay
                await asyncio.sleep(delay_seconds)
                
                mock_response = Mock()
                mock_response.choices = [Mock()]
                
                # Return appropriate mock responses based on prompt
                prompt = kwargs['messages'][1]['content']
                if 'extract the main topics' in prompt.lower():
                    mock_response.choices[0].message.content = '["Creative Business", "Art Projects", "Content Creation"]'
                elif 'extract planning elements' in prompt.lower():
                    mock_response.choices[0].message.content = '''
                    {
                        "schedules": ["Daily art practice", "Weekly planning"],
                        "checklists": ["Project checklist", "Supply inventory"],
                        "trackers": ["Project tracker", "Time tracker"],
                        "workflows": ["Creative workflow", "Client workflow"]
                    }
                    '''
                elif 'extract user preferences' in prompt.lower():
                    mock_response.choices[0].message.content = '''
                    {
                        "aesthetic_style": ["dreamy", "colorful", "kawaii"],
                        "colors": ["pink", "lavender", "mint green"],
                        "organization_style": ["visual", "project-based"],
                        "features_requested": ["content calendar", "project tracker", "client database"]
                    }
                    '''
                elif 'extract concrete action items' in prompt.lower():
                    mock_response.choices[0].message.content = '["Create content calendar", "Set up project tracker", "Organize supplies"]'
                elif 'organizational structure' in prompt.lower():
                    mock_response.choices[0].message.content = '''
                    {
                        "main_categories": ["Projects", "Clients", "Content", "Inventory"],
                        "database_types": ["project_tracker", "client_database", "content_calendar", "inventory_system"],
                        "view_types": ["kanban", "calendar", "gallery", "table"],
                        "page_types": ["dashboard", "templates", "mood_boards"]
                    }
                    '''
                else:
                    mock_response.choices[0].message.content = '[]'
                
                return mock_response
            
            mock_client.chat.completions.create = AsyncMock(side_effect=mock_create)
            return ConversationAnalyzer()
    
    async def benchmark_parallel_execution(self, analyzer, iterations=5):
        """Benchmark the current parallel implementation"""
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            result = await analyzer.analyze(self.sample_conversation)
            execution_time = time.time() - start_time
            times.append(execution_time)
            
            # Verify result completeness
            assert "topics" in result
            assert "planning_elements" in result
            assert "user_preferences" in result
            assert "action_items" in result
            assert "structure" in result
        
        return {
            "times": times,
            "average": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    async def benchmark_sequential_execution(self, analyzer, iterations=5):
        """Benchmark sequential execution for comparison"""
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            # Sequential execution (not using asyncio.gather)
            cleaned_text = analyzer._preprocess_text(self.sample_conversation)
            topics = await analyzer.extract_topics(cleaned_text)
            planning_elements = await analyzer.identify_planning_elements(cleaned_text)
            user_preferences = await analyzer.detect_user_preferences(cleaned_text)
            action_items = await analyzer.extract_action_items(cleaned_text)
            structure = await analyzer.extract_structure(cleaned_text)
            
            # Combine results (same as parallel version)
            result = {
                "topics": topics,
                "planning_elements": planning_elements,
                "user_preferences": user_preferences,
                "action_items": action_items,
                "structure": structure
            }
            
            execution_time = time.time() - start_time
            times.append(execution_time)
            
            # Verify result completeness
            assert "topics" in result
            assert len(result["topics"]) > 0
        
        return {
            "times": times,
            "average": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    async def run_benchmark(self, api_delay=0.1, iterations=5):
        """Run complete benchmark comparing parallel vs sequential"""
        print(f"🚀 Running Performance Benchmark")
        print(f"   API Delay Simulation: {api_delay}s per call")
        print(f"   Iterations: {iterations}")
        print(f"   Total API calls per test: 5 (topics, planning, preferences, actions, structure)")
        print()
        
        analyzer = self.create_mock_analyzer(delay_seconds=api_delay)
        
        # Benchmark parallel execution
        print("⚡ Testing Parallel Execution (Current Implementation)...")
        parallel_stats = await self.benchmark_parallel_execution(analyzer, iterations)
        
        # Benchmark sequential execution
        print("🐌 Testing Sequential Execution (For Comparison)...")
        sequential_stats = await self.benchmark_sequential_execution(analyzer, iterations)
        
        # Calculate performance improvement
        improvement_percent = ((sequential_stats["average"] - parallel_stats["average"]) / sequential_stats["average"]) * 100
        speedup_factor = sequential_stats["average"] / parallel_stats["average"]
        
        # Display results
        print("\n" + "="*60)
        print("📊 BENCHMARK RESULTS")
        print("="*60)
        
        print(f"\n🔄 PARALLEL EXECUTION:")
        print(f"   Average time: {parallel_stats['average']:.3f}s")
        print(f"   Median time:  {parallel_stats['median']:.3f}s")
        print(f"   Min time:     {parallel_stats['min']:.3f}s")
        print(f"   Max time:     {parallel_stats['max']:.3f}s")
        print(f"   Std dev:      {parallel_stats['std_dev']:.3f}s")
        
        print(f"\n⏳ SEQUENTIAL EXECUTION:")
        print(f"   Average time: {sequential_stats['average']:.3f}s")
        print(f"   Median time:  {sequential_stats['median']:.3f}s")
        print(f"   Min time:     {sequential_stats['min']:.3f}s")
        print(f"   Max time:     {sequential_stats['max']:.3f}s")
        print(f"   Std dev:      {sequential_stats['std_dev']:.3f}s")
        
        print(f"\n🎯 PERFORMANCE IMPROVEMENT:")
        print(f"   Speedup factor:    {speedup_factor:.2f}x")
        print(f"   Time reduction:    {improvement_percent:.1f}%")
        print(f"   Time saved:        {sequential_stats['average'] - parallel_stats['average']:.3f}s per analysis")
        
        # Theoretical vs actual improvement
        theoretical_speedup = 5.0  # 5 functions running in parallel
        efficiency = (speedup_factor / theoretical_speedup) * 100
        
        print(f"\n🧮 THEORETICAL ANALYSIS:")
        print(f"   Theoretical max speedup: {theoretical_speedup:.1f}x (5 parallel functions)")
        print(f"   Actual efficiency:       {efficiency:.1f}%")
        print(f"   Overhead factor:         {theoretical_speedup / speedup_factor:.2f}x")
        
        # Recommendations
        print(f"\n💡 INSIGHTS:")
        if speedup_factor >= 3.0:
            print("   ✅ Excellent parallel performance! Significant time savings achieved.")
        elif speedup_factor >= 2.0:
            print("   ✅ Good parallel performance. Notable improvement over sequential execution.")
        elif speedup_factor >= 1.5:
            print("   ⚠️  Moderate improvement. Consider optimizing async operations.")
        else:
            print("   ❌ Limited improvement. Check for synchronous bottlenecks.")
        
        # Real-world impact
        daily_analyses = 100
        daily_time_saved = (sequential_stats['average'] - parallel_stats['average']) * daily_analyses
        yearly_time_saved = daily_time_saved * 365 / 3600  # Convert to hours
        
        print(f"\n🌍 REAL-WORLD IMPACT:")
        print(f"   For {daily_analyses} analyses/day:")
        print(f"   Daily time saved:   {daily_time_saved:.1f} seconds ({daily_time_saved/60:.1f} minutes)")
        print(f"   Yearly time saved:  {yearly_time_saved:.1f} hours")
        
        return {
            "parallel": parallel_stats,
            "sequential": sequential_stats,
            "speedup_factor": speedup_factor,
            "improvement_percent": improvement_percent
        }
    
    async def run_load_test(self, concurrent_requests=10, api_delay=0.05):
        """Test performance under concurrent load"""
        print(f"\n🏋️ Load Test: {concurrent_requests} concurrent requests")
        print(f"   API Delay: {api_delay}s per call")
        
        analyzer = self.create_mock_analyzer(delay_seconds=api_delay)
        
        # Create concurrent tasks
        tasks = []
        for i in range(concurrent_requests):
            task = analyzer.analyze(f"{self.sample_conversation} Request {i+1}")
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Verify all requests completed successfully
        successful_requests = sum(1 for result in results if "topics" in result)
        
        print(f"   ✅ Completed: {successful_requests}/{concurrent_requests} requests")
        print(f"   ⏱️  Total time: {total_time:.3f}s")
        print(f"   📊 Requests/sec: {concurrent_requests / total_time:.2f}")
        print(f"   📈 Avg per request: {total_time / concurrent_requests:.3f}s")
        
        return {
            "concurrent_requests": concurrent_requests,
            "successful_requests": successful_requests,
            "total_time": total_time,
            "requests_per_second": concurrent_requests / total_time,
            "average_per_request": total_time / concurrent_requests
        }


async def main():
    """Run all benchmarks"""
    benchmark = PerformanceBenchmark()
    
    # Run main benchmark
    results = await benchmark.run_benchmark(api_delay=0.1, iterations=5)
    
    # Run load test
    await benchmark.run_load_test(concurrent_requests=10, api_delay=0.05)
    
    print("\n" + "="*60)
    print("🎉 Benchmark Complete!")
    print("\nKey Takeaways:")
    print("• The enhanced analyzer uses asyncio.gather() for parallel execution")
    print("• All 5 extraction functions run simultaneously, not sequentially")
    print("• This provides significant performance improvements for API-bound operations")
    print("• The system maintains high reliability with proper error handling")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())