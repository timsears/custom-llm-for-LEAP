from flask import Flask, request, jsonify
import os
import openai
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

app = Flask(__name__)

# Check if running on Vercel or locally
# Initialize the Translate client with the obtained credentials
if 'GOOGLE_APPLICATION_CREDENTIALS_BASE64' in os.environ:
    # Vercel deployment: decode credentials from Base64
    credentials_base64 = os.environ['GOOGLE_APPLICATION_CREDENTIALS_BASE64']
    credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
    credentials = service_account.Credentials.from_service_account_info(json.loads(credentials_json))
    translate_client = translate.Client(credentials=credentials)
elif 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    # Local development: load credentials from JSON file
    translate_client = translate.Client()
else:
    raise Exception('Google Cloud credentials missing.')

openai.api_key = os.getenv('OPENAI_API_KEY')

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
