# chatbot/services.py
import requests
import random
import time
from django.conf import settings

def get_ai_response(messages):
    """
    Get response from Hugging Face API with fallback to mock responses.
    """
    try:
        # Prepare the prompt from messages
        prompt = ""
        for msg in messages:
            if msg["role"] == "user":
                prompt += f"Human: {msg['content']}\n"
            else:
                prompt += f"Assistant: {msg['content']}\n"
        prompt += "Assistant: "
        
        # Call Hugging Face API
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 250,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        print(f"Calling Hugging Face API with prompt length: {len(prompt)}")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0 and "generated_text" in response_data[0]:
                return response_data[0]["generated_text"].strip()
            return "Received response but couldn't parse it."
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return get_mock_response(messages)
    
    except Exception as e:
        print(f"Error with Hugging Face API: {str(e)}")
        return get_mock_response(messages)

def get_mock_response(messages):
    """Provide mock responses as fallback."""
    last_message = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_message = msg["content"]
            break
    
    responses = [
        f"This is a response to: '{last_message}'. I'm your Genius assistant running in mock mode due to API issues.",
        f"I understand you're asking about '{last_message}'. Let me help you with that... (fallback mode)",
        "I'm Genius, your personal AI assistant. I can help with coding, life advice, and more! (API offline)",
        f"Good question about '{last_message}'. Here's what I think... (mock response)",
        "Your application is working in fallback mode due to API connection issues."
    ]
    
    time.sleep(1)  # Simulate processing time
    return random.choice(responses)