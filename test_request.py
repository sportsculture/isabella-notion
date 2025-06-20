#!/usr/bin/env python3
"""
Test HTTP requests to Isabella Notion API
"""

import requests
import json
import subprocess
import time
import os
import signal
from pathlib import Path

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting server...")
    
    # Change to src directory and start server
    src_dir = Path(__file__).parent / "src"
    process = subprocess.Popen(
        ["python", "main.py"],
        cwd=src_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server started successfully")
            return process
        else:
            print("❌ Server not responding properly")
            return None
    except requests.exceptions.RequestException:
        print("❌ Server failed to start")
        return None

def test_conversation_analysis():
    """Test the conversation analysis endpoint"""
    print("\n🧪 Testing conversation analysis...")
    
    # Sample conversation
    conversation = """
    Hey, I want help with my YouTube channel. I want to be more consistent and 
    plan better. I need a content calendar, filming checklist, and want everything 
    to look dreamy and colorful with a kawaii aesthetic.
    """
    
    payload = {
        "conversation": conversation
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze-conversation",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis successful!")
            print(f"📊 Topics: {result.get('topics', [])}")
            print(f"🎨 Style: {result.get('user_preferences', {}).get('aesthetic_style', [])}")
            print(f"📋 Database types: {result.get('structure', {}).get('database_types', [])}")
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def main():
    """Run the HTTP tests"""
    print("🌸 Isabella Notion - HTTP API Testing\n")
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Could not start server for testing")
        return False
    
    try:
        # Test the endpoints
        success = test_conversation_analysis()
        
        print("\n" + "="*50)
        if success:
            print("🎉 HTTP API tests passed! Ready for production.")
            print("\n📖 API Documentation: http://localhost:8000/docs")
        else:
            print("❌ Some HTTP tests failed.")
        
        return success
        
    finally:
        # Stop the server
        print("\n🛑 Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("✅ Server stopped")

if __name__ == "__main__":
    main()