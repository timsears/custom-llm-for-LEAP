'''
`python test_llm.py --dev` or `--prod` 
'''

import requests
import json
import argparse

# Define command line argument parsing
parser = argparse.ArgumentParser(description='Test LLM API.')
parser.add_argument('--dev', action='store_true', help='Use local dev environment URL.')
parser.add_argument('--prod', action='store_true', help='Use production environment URL.')

args = parser.parse_args()

# Set the domain URL based on the command line argument
if args.dev:
    DOMAIN_URL = "http://127.0.0.1:5000"
elif args.prod:
    DOMAIN_URL = "https://custom-llm-for-leap.vercel.app"
else:
    raise ValueError("Please specify either --test or --prod option.")

groq_model = "mixtral-8x7b-32768"
openai_model = "gpt-3.5-turbo"
### CHANGE AS NEEDED 
#test_model = groq_model
test_model = openai_model

def test_llm_single_message():
    print("Test 1: Single Message Translation")
    endpoint = f"{DOMAIN_URL}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    # Single message in Arabic
    messages = [
        {"role": "user", "content": "مرحبا، كيف حالك؟"}
    ]
    
    payload = {
        "model": test_model,
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
        "model": test_model,
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
