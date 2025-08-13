#!/usr/bin/env python3
"""
Simple test script to verify TWAIN AI Backend API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_persona_endpoint():
    """Test the persona creation endpoint"""
    print("Testing /persona endpoint...")
    
    data = {
        "url": "https://example.com",
        "description": "Test persona generation"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/persona", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

def test_ideas_endpoint():
    """Test the ideas generation endpoint"""
    print("\nTesting /ideas endpoint...")
    
    # Create a sample persona
    persona = {
        "id": "test_lead",
        "name": "Test Company",
        "company": "Test Corp",
        "pain_points": ["High costs", "Inefficient processes"],
        "social_proof": [],
        "cost_of_inaction": ["Lost revenue"],
        "solutions": ["AI optimization"],
        "objections": ["Budget constraints"],
        "competitive_advantages": ["Faster implementation"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ideas", json=persona)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

def test_campaign_endpoint():
    """Test the campaign creation endpoint"""
    print("\nTesting /create_campaign endpoint...")
    
    # Create a sample campaign request
    campaign_request = {
        "persona": {
            "id": "test_lead",
            "name": "Test Company",
            "company": "Test Corp",
            "pain_points": ["High costs", "Inefficient processes"],
            "social_proof": [],
            "cost_of_inaction": ["Lost revenue"],
            "solutions": ["AI optimization"],
            "objections": ["Budget constraints"],
            "competitive_advantages": ["Faster implementation"]
        },
        "outreach_channel": "email"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/create_campaign", json=campaign_request)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

def test_health_check():
    """Test if the server is running"""
    print("Testing server health...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Server is running and accessible")
        else:
            print(f"Server responded with status: {response.status_code}")
    except Exception as e:
        print(f"Server connection failed: {e}")

if __name__ == "__main__":
    print("TWAIN AI Backend API Test")
    print("=" * 40)
    
    test_health_check()
    test_persona_endpoint()
    test_ideas_endpoint()
    test_campaign_endpoint()
    
    print("\nTest completed!")

