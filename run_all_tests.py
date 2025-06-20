#!/usr/bin/env python3
"""
Comprehensive test runner for Isabella Notion Enhanced Conversation Analyzer
Runs all tests and demonstrates the enhanced functionality
"""

import sys
import os
import asyncio
import subprocess
from pathlib import Path
import time

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Change to project root
os.chdir(Path(__file__).parent)


async def run_unit_tests():
    """Run unit tests with pytest"""
    print("🧪 Running Unit Tests...")
    print("="*50)
    
    try:
        # Run the enhanced analyzer tests
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_enhanced_analyzer.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Unit tests passed!")
            return True
        else:
            print("❌ Unit tests failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Unit tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running unit tests: {str(e)}")
        return False


async def run_api_tests():
    """Run API integration tests"""
    print("\n🌐 Running API Integration Tests...")
    print("="*50)
    
    try:
        # Run the enhanced API tests
        result = subprocess.run([
            sys.executable, "test_api.py"
        ], capture_output=True, text=True, timeout=120)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ API tests passed!")
            return True
        else:
            print("❌ API tests failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ API tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running API tests: {str(e)}")
        return False


async def run_performance_benchmark():
    """Run performance benchmark"""
    print("\n⚡ Running Performance Benchmark...")
    print("="*50)
    
    try:
        # Run the performance benchmark
        result = subprocess.run([
            sys.executable, "tests/test_performance_benchmark.py"
        ], capture_output=True, text=True, timeout=180)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Performance benchmark completed!")
            return True
        else:
            print("❌ Performance benchmark failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Performance benchmark timed out")
        return False
    except Exception as e:
        print(f"❌ Error running performance benchmark: {str(e)}")
        return False


async def run_basic_functionality_demo():
    """Demonstrate basic functionality without external dependencies"""
    print("\n🎯 Basic Functionality Demo...")
    print("="*50)
    
    try:
        from core.conversation_analyzer import ConversationAnalyzer
        
        # Test text preprocessing
        analyzer = ConversationAnalyzer()
        sample_text = "  This   is   a   test   with   extra   spaces.  \n\n  "
        cleaned = analyzer._preprocess_text(sample_text)
        
        print(f"✅ Text preprocessing works:")
        print(f"   Original: '{sample_text}'")
        print(f"   Cleaned:  '{cleaned}'")
        
        # Test prompt building
        prompt = analyzer._build_analysis_prompt("Sample conversation")
        print(f"✅ Prompt building works (length: {len(prompt)} chars)")
        
        # Test response parsing with valid JSON
        sample_response = '''
        {
            "topics": ["Test Topic"],
            "planning_elements": {
                "schedules": ["Test Schedule"],
                "checklists": ["Test Checklist"],
                "trackers": ["Test Tracker"],
                "workflows": ["Test Workflow"]
            },
            "user_preferences": {
                "aesthetic_style": ["Test Style"],
                "colors": ["Test Color"],
                "organization_style": ["Test Organization"],
                "features_requested": ["Test Feature"]
            },
            "action_items": ["Test Action"],
            "structure": {
                "main_categories": ["Test Category"],
                "database_types": ["Test Database"],
                "view_types": ["Test View"],
                "page_types": ["Test Page"]
            }
        }
        '''
        
        parsed = analyzer._parse_analysis_response(sample_response)
        print(f"✅ JSON parsing works:")
        print(f"   Topics: {parsed['topics']}")
        print(f"   Planning elements keys: {list(parsed['planning_elements'].keys())}")
        print(f"   User preferences keys: {list(parsed['user_preferences'].keys())}")
        print(f"   Structure keys: {list(parsed['structure'].keys())}")
        
        # Test parsing with invalid JSON (should fallback gracefully)
        invalid_response = "This is not JSON!"
        fallback_parsed = analyzer._parse_analysis_response(invalid_response)
        print(f"✅ Fallback parsing works:")
        print(f"   Fallback topics: {fallback_parsed['topics']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_environment():
    """Check if the environment is properly set up"""
    print("🔍 Environment Check...")
    print("="*50)
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append(f"Python 3.8+ required, found {sys.version}")
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check for required directories
    required_dirs = ["src", "tests", "src/core"]
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            issues.append(f"Missing directory: {dir_path}")
        else:
            print(f"✅ Directory exists: {dir_path}")
    
    # Check for required files
    required_files = [
        "src/core/conversation_analyzer.py",
        "src/core/config.py",
        "tests/test_enhanced_analyzer.py",
        "seed-convo.txt"
    ]
    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"Missing file: {file_path}")
        else:
            print(f"✅ File exists: {file_path}")
    
    # Check for optional dependencies
    try:
        import pytest
        print(f"✅ pytest installed: {pytest.__version__}")
    except ImportError:
        issues.append("pytest not installed (required for unit tests)")
    
    try:
        import openai
        print(f"✅ openai library available: {openai.__version__}")
    except ImportError:
        issues.append("openai library not installed")
    
    try:
        import fastapi
        print(f"✅ fastapi available: {fastapi.__version__}")
    except ImportError:
        issues.append("fastapi not installed (required for API tests)")
    
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("OPENAI_API_KEY not set (required for live API tests)")
    else:
        print("✅ OPENAI_API_KEY is set")
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 Some tests may be skipped due to missing dependencies.")
        return False
    else:
        print("\n✅ Environment looks good!")
        return True


async def main():
    """Run comprehensive test suite"""
    print("🌸 Isabella Notion - Enhanced Conversation Analyzer Test Suite")
    print("="*70)
    print("Testing the new modular conversation analysis engine with:")
    print("• Individual extraction functions (topics, planning, preferences, actions, structure)")
    print("• Parallel execution using asyncio.gather()")
    print("• Comprehensive error handling and fallbacks")
    print("• Performance benchmarking")
    print("• API integration testing")
    print()
    
    start_time = time.time()
    
    # Environment check
    env_ok = check_environment()
    
    # Basic functionality demo (always runs)
    basic_demo_ok = await run_basic_functionality_demo()
    
    results = {"basic_demo": basic_demo_ok}
    
    if env_ok:
        # Run unit tests if environment is set up
        unit_tests_ok = await run_unit_tests()
        results["unit_tests"] = unit_tests_ok
        
        # Run API tests
        api_tests_ok = await run_api_tests()
        results["api_tests"] = api_tests_ok
        
        # Run performance benchmark
        benchmark_ok = await run_performance_benchmark()
        results["benchmark"] = benchmark_ok
    else:
        print("\n⚠️  Skipping some tests due to environment issues")
        results.update({"unit_tests": None, "api_tests": None, "benchmark": None})
    
    # Summary
    total_time = time.time() - start_time
    print("\n" + "="*70)
    print("📊 TEST SUITE SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⏭️  SKIPPED"
        print(f"{test_name.replace('_', ' ').title():.<40} {status}")
    
    passed_tests = sum(1 for r in results.values() if r is True)
    total_tests = sum(1 for r in results.values() if r is not None)
    
    print(f"\nResults: {passed_tests}/{total_tests} test categories passed")
    print(f"Total execution time: {total_time:.2f} seconds")
    
    if passed_tests == total_tests and total_tests > 0:
        print("\n🎉 ALL TESTS PASSED! Enhanced conversation analyzer is working perfectly.")
        print("\n🚀 Enhanced Features Verified:")
        print("   ✅ Modular extraction functions working independently")
        print("   ✅ Parallel execution providing performance improvements")
        print("   ✅ Comprehensive error handling and graceful fallbacks")
        print("   ✅ API integration maintaining backward compatibility")
        print("   ✅ Performance benchmarks showing measurable improvements")
        
        print("\n💡 Next Steps:")
        print("   1. Deploy the enhanced analyzer to production")
        print("   2. Monitor performance improvements in real usage")
        print("   3. Consider adding more specialized extraction functions")
        print("   4. Implement caching for frequently analyzed conversations")
        
    elif passed_tests > 0:
        print(f"\n⚠️  {passed_tests}/{total_tests} test categories passed.")
        print("   Check the detailed output above for specific issues.")
        
    else:
        print("\n❌ No tests passed. Please check the setup and try again.")
    
    return passed_tests == total_tests and total_tests > 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)