#!/usr/bin/env python3
"""
Test script for multilingual construction assistant
Demonstrates language detection and response capabilities
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"

def test_language_detection():
    """Test language detection with different inputs"""
    print("🧪 Testing Language Detection")
    print("=" * 50)
    
    test_cases = [
        {
            "question": "What materials do I need for a residential extension in Singapore?",
            "expected_lang": "en",
            "description": "English construction question (Singapore)"
        },
        {
            "question": "香港住宅擴建需要什麼材料？",
            "expected_lang": "zh-tw", 
            "description": "Traditional Chinese construction question (Hong Kong)"
        },
        {
            "question": "新加坡住宅扩建需要什么材料？",
            "expected_lang": "zh-cn",
            "description": "Simplified Chinese construction question (Singapore)"
        },
        {
            "question": "Anong mga materyales ang kailangan para sa residential extension sa Pilipinas?",
            "expected_lang": "tl",
            "description": "Tagalog construction question (Philippines)"
        },
        {
            "question": "Apakah bahan-bahan yang diperlukan untuk pembesaran rumah di Malaysia?",
            "expected_lang": "ms",
            "description": "Malay construction question (Malaysia)"
        },
        {
            "question": "What are the UK building regulations for extensions?",
            "expected_lang": "en",
            "description": "English regulatory question (UK)"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Input: {test_case['question']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                json={
                    "question": test_case['question'],
                    "use_context": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result.get('detected_language', 'unknown')
                answer = result.get('answer', 'No answer received')
                
                print(f"   Detected Language: {detected_lang}")
                print(f"   Expected: {test_case['expected_lang']}")
                print(f"   Match: {'✅' if detected_lang == test_case['expected_lang'] else '❌'}")
                print(f"   Answer: {answer[:100]}...")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        time.sleep(1)  # Rate limiting

def test_supported_languages():
    """Test the languages endpoint"""
    print("\n🌐 Testing Supported Languages Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/languages")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Languages endpoint working")
            print(f"Supported languages: {len(result['supported_languages'])}")
            
            for lang in result['supported_languages']:
                print(f"   - {lang['name']} ({lang['native_name']}) - {lang['code']}")
                
            print(f"Auto-detection available: {result['auto_detection']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_manual_language_specification():
    """Test manual language specification"""
    print("\n🎯 Testing Manual Language Specification")
    print("=" * 50)
    
    test_cases = [
        {
            "question": "What materials are needed for construction in Malaysia?",
            "language": "ms",
            "description": "English question with Malay specification"
        },
        {
            "question": "建築材料有哪些？",
            "language": "en", 
            "description": "Chinese question with English specification"
        },
        {
            "question": "Anong mga materyales ang kailangan para sa construction?",
            "language": "tl",
            "description": "Tagalog question with Tagalog specification"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Input: {test_case['question']}")
        print(f"   Specified Language: {test_case['language']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                json={
                    "question": test_case['question'],
                    "language": test_case['language'],
                    "use_context": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result.get('detected_language', 'unknown')
                answer = result.get('answer', 'No answer received')
                
                print(f"   Used Language: {detected_lang}")
                print(f"   Answer: {answer[:100]}...")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        time.sleep(1)

def main():
    """Run all tests"""
    print("🏗️ Construction Assistant Multilingual Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not responding properly")
            return
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the Flask server is running on localhost:5000")
        return
    
    # Run tests
    test_supported_languages()
    test_language_detection()
    test_manual_language_specification()
    
    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    main() 