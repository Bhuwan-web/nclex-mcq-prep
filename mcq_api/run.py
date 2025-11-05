#!/usr/bin/env python3
"""
Simple script to run the NCLEX MCQ Practice API
"""
import uvicorn
import os
import sys

# Add the parent directory to the path so we can import the mcq_api module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_database():
    """Check if the database file exists"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nclex_simple.db")
    if not os.path.exists(db_path):
        print(f"⚠️  Warning: Database file not found at {db_path}")
        print("   Please run the extraction scripts first to create the database.")
        return False
    else:
        print(f"✅ Database found at {db_path}")
        return True


if __name__ == "__main__":
    print("🚀 Starting NCLEX MCQ Practice API...")
    print("=" * 50)

    # Check database
    check_database()

    print("\n📍 Server Information:")
    print("   API Base URL: http://localhost:8000")
    print("   Interactive Docs: http://localhost:8000/docs")
    print("   Web Interface: http://localhost:8000")
    print("   Health Check: http://localhost:8000/health")
    print("\n⚡ Starting server...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)

    try:
        uvicorn.run("mcq_api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)
