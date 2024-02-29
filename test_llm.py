import requests
import json

# Replace this URL with your Flask application's URL
DOMAIN_URL = "http://127.0.0.1:5000"
#DOMAIN_URL = "https://custom-llm-for-leap.vercel.app"

def test_llm_single_message():
    print("Test 1: Single Message Translation")
    endpoint = f"{DOMAIN_URL}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    # Single message in Arabic
    messages = [
        {"role": "user", "content": "مرحبا، كيف حالك؟"}
    ]
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages
    }
    
    response = requests.post(endpoint, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("Input Messages:")
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        print("Response:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"Failed to get response: {response.status_code}")

def test_llm_conversation():
    print("\nTest 2: Conversation Translation")
    endpoint = f"{DOMAIN_URL}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    # A simulated conversation with multiple exchanges
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "ما هو الطقس اليوم؟"},
        {"role": "assistant", "content": "Let me check that for you."},
        {"role": "user", "content": "شكرا لك"}
    ]
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages
    }
    
    response = requests.post(endpoint, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("Input Messages:")
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        print("Response:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"Failed to get response: {response.status_code}")

if __name__ == "__main__":
    test_llm_single_message()
    test_llm_conversation()
