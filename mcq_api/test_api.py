#!/usr/bin/env python3
"""
Simple test script to verify API endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_endpoint(endpoint, description):
    """Test a single endpoint"""
    try:
        print(f"\n🧪 Testing {description}")
        print(f"   URL: {BASE_URL}{endpoint}")

        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   Result: List with {len(data)} items")
                if len(data) > 0:
                    print(f"   Sample: {json.dumps(data[0], indent=2)[:200]}...")
            else:
                print(f"   Result: {json.dumps(data, indent=2)[:200]}...")
            print("   ✅ SUCCESS")
        else:
            print(f"   Error: {response.text}")
            print("   ❌ FAILED")

    except Exception as e:
        print(f"   Exception: {e}")
        print("   ❌ FAILED")


def main():
    print("🚀 Testing NCLEX MCQ Practice API")
    print("=" * 50)

    # Test all endpoints
    endpoints = [
        ("/health", "Health Check"),
        ("/stats/", "Database Statistics"),
        ("/questions/?page=1", "Questions (Page 1)"),
        ("/questions-with-answers/?page=1", "Questions with Answers"),
        ("/practice-mistakes/", "Practice Mistakes"),
        ("/report/", "Performance Report"),
        ("/sessions/", "Practice Sessions"),
        ("/mistakes/", "All Mistakes"),
    ]

    for endpoint, description in endpoints:
        test_endpoint(endpoint, description)

    print("\n" + "=" * 50)
    print("🏁 API Testing Complete")


if __name__ == "__main__":
    main()
