from flask import Flask, request, jsonify, Response
import os
from openai import OpenAI
import json
import base64
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
from groq import Groq
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

groq_key = os.environ.get('GROQ_API_KEY')

@app.route('/', methods=['GET'])
def health_check():
    return 'Server is up and running!', 200


@app.route('/chat/completions', methods=['POST'])
def chat_completions():
    data = request.get_json()
    model = data.get('model', 'gpt-3.5-turbo') #

    if model == 'gpt-3.5-turbo':
        client = OpenAI()
    elif model == 'mixtral-8x7b-32768':
        client = OpenAI( api_key=groq_key, base_url='https://api.groq.com/openai/v1')
    else:
       return "chat_completions: Unsupported model: " + model , 400
       #raise Exception ("chat_completions: Unsupported model: ", model)

    print("\nmodel: " + model)

    messages = data.get('messages', [])

    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    # DONT TRANSLATE INCOMING
    # print("\nincoming messages:\n")
    # for message in messages:
        # print("... " + message['content'])
        # if message['role'] == 'user':
        #     detected_lang = translate_client.detect_language(message['content'])['language']
        #     if detected_lang != 'en':
        #         x = translate_client.translate(
        #             message['content'],
        #             source_language = 'ar',
        #             target_language='en',
        #             model='nmt')['translatedText']
        #         message['content'] = x
        #         print("translated content: " + x)

    # print what the llm will be responding to
    ms = [m for m in messages if m['content'] == 'user']
    if ms: print ("\nlast user input", ms[-1])

    # Call OpenAI's completion API with the translated conversation
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    completion_text = (response.choices)[0].message.content
    #print("\nraw llm response:\n", response)
    print("\nllm response: " + completion_text)

    # if detected_lang != 'en':
    #     completion_translated = translate_client.translate(completion_text, target_language='ar', format_='text', model='nmt')['translatedText']
    # else:
    #     completion_translated = completion_text

    # DO Translate response to Arabic
    target_language = 'ar'
    completion_translated = translate_client.translate(completion_text, target_language='ar', format_='text', model='nmt')['translatedText']
    print("\ntranslated llm response: ", completion_translated)

    # Construct and return the response object
    llm_response = {
        "id": response.id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "system_fingerprint": None,
        "choices": [{
            "index": 0,
            "delta": {"content": completion_translated},
            "logprobs": None,
            "finish_reason": "stop"
        }]
    }

    #print ("\n",llm_response)

    # Convert message into data packet.
    def generate(message):
        json_data = json.dumps(message)
        yield f"data: {json_data}\n\n"

    # Stream response back.
    return Response(generate(llm_response), content_type='text/event-stream')
