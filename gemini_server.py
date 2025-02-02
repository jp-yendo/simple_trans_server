import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from flask import Flask, request

load_dotenv()
model_name = os.getenv("GEMINI_MODEL_NAME")
api_key = os.getenv("GEMINI_API_KEY")
listen_address = os.getenv("LISTEN_ADDRESS")
listen_port = os.getenv("LISTEN_PORT")
default_from_language = os.getenv("DEFAULT_FROM_LANGUAGE")
default_to_language = os.getenv("DEFAULT_TO_LANGUAGE")

# Verify all required settings are configured
if not all([model_name, api_key, listen_address, listen_port, default_from_language, default_to_language]):
    raise ValueError("""
    Missing required environment variables:
    GEMINI_MODEL_NAME
    GEMINI_API_KEY
    LISTEN_ADDRESS
    LISTEN_PORT
    DEFAULT_FROM_LANGUAGE
    DEFAULT_TO_LANGUAGE
    Please check your .env file.
    """)

# Validate port number is in valid range
try:
    listen_port = int(listen_port)
    if not (0 <= listen_port <= 65535):
        raise ValueError
except ValueError as exc:
    raise ValueError("LISTEN_PORT must be a valid port number between 0-65535") from exc

# Configure the API key
genai.configure(api_key=api_key)

# Create the model
generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name=model_name,
    generation_config=generation_config,
)

# Create the Flask app
app = Flask(__name__)

# Define the translation route
@app.route('/translate', methods=['get'])

def translate():
    # get parameters from request
    lang_from = request.args.get('from', default_from_language)
    lang_to = request.args.get('to', default_to_language)
    content = request.args.get('text')
    if content is None:
        return "Error: Missing required parameter 'text'", 400

    # create chat session
    chat_session = model.start_chat(history=[])

    # create message
    message = f"""You are a professional,authentic translation engine,only returns translations.\n
For example:\n
<Start>\n
Hello <Keep This Symbol>\n
World <Keep This Symbol>\n
<End>\n
The translation is:\n
<Start>\n
こんにちわ <Keep This Symbol>\n
世界 <Keep This Symbol>\n
<End>\n
\n
Translate the content to {lang_from} into {lang_to}:\n
\n
<Start>{content}<End>"""

    # send message
    response = chat_session.send_message(message)

    # remove start and end tags
    trans = re.sub(r"<Start>|<End>", "", response.text)

    # return translation
    return trans

# Run the Flask app
if __name__ == '__main__':
    app.run(host=listen_address, port=listen_port)
