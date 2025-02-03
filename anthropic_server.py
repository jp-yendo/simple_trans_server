import os
import re
from dotenv import load_dotenv
import anthropic
from flask import Flask, request
from langcodes import Language

load_dotenv()
model_name = os.getenv("ANTHROPIC_MODEL_NAME")
api_key = os.getenv("ANTHROPIC_API_KEY")
listen_address = os.getenv("LISTEN_ADDRESS")
listen_port = os.getenv("LISTEN_PORT")
default_from_language = os.getenv("DEFAULT_FROM_LANGUAGE")
default_to_language = os.getenv("DEFAULT_TO_LANGUAGE")

# Verify all required settings are configured
if not all([model_name, api_key, listen_address, listen_port, default_from_language, default_to_language]):
    raise ValueError("""
    Missing required environment variables:
    ANTHROPIC_MODEL_NAME
    ANTHROPIC_API_KEY
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

    # convert lang_from and lang_to to language names
    lang_from = Language.get(lang_from).display_name()
    lang_to = Language.get(lang_to).display_name()

    # create message
    system_message = "You are a professional,authentic translation engine,only returns translations."
    user_message = f"""For example:\n
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

    # create client
    client = anthropic.Anthropic(api_key=api_key)

    # send message
    response = client.messages.create(
        model=model_name,
        max_tokens=1000,
        system=system_message,
        messages=[{"role": "user", "content": user_message}],
    )

    # remove start and end tags
    trans = re.sub(r"<Start>|<End>", "", response.content[0].text)

    # return translation
    return trans

# Run the Flask app
if __name__ == '__main__':
    app.run(host=listen_address, port=listen_port)
