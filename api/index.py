from flask import Flask, request, jsonify
import os
import openai
from google.cloud import translate_v2 as translate

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
# Verify that the environment variable is set
google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if not google_credentials_path or not os.path.exists(google_credentials_path):
    raise Exception("Failed to find Google application credentials.", google_credentials_path)


translate_client = translate.Client()

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.get_json()
    model = data.get('model', 'gpt-3.5-turbo')
    messages = data.get('messages', [])

    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    # Translate all user messages to English
    for message in messages:
        if message['role'] == 'user':
            detected_lang = translate_client.detect_language(message['content'])['language']
            if detected_lang != 'en':
                message['content'] = translate_client.translate(message['content'], target_language='en', model='nmt')['translatedText']

    # Call OpenAI's completion API with the translated conversation
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )

    # Assuming response should be translated back to the original language if needed
    completion_text = response.choices[0].message['content']
    if detected_lang != 'en':
        completion_translated = translate_client.translate(completion_text, target_language=detected_lang, format_='text', model='nmt')['translatedText']
    else:
        completion_translated = completion_text

    # Construct and return the response object
    response_data = {
        'id': response['id'],
        'model': response['model'],
        'choices': [{
            'message': {'role': 'assistant', 'content': completion_translated},
        }]
    }

    return jsonify(response_data)
