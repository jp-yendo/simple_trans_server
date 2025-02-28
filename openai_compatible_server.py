import os
import re
import requests
from dotenv import load_dotenv
from flask import Flask, request
from langcodes import Language

load_dotenv(override=True)
base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL")
model_name = os.getenv("OPENAI_COMPATIBLE_MODEL_NAME")
api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY")
listen_address = os.getenv("LISTEN_ADDRESS")
listen_port = os.getenv("LISTEN_PORT")
default_from_language = os.getenv("DEFAULT_FROM_LANGUAGE")
default_to_language = os.getenv("DEFAULT_TO_LANGUAGE")

# Verify all required settings are configured
if not all([base_url, model_name, listen_address, listen_port, default_from_language, default_to_language]):
    raise ValueError("""
    Missing required environment variables:
    OPENAI_COMPATIBLE_BASE_URL
    OPENAI_COMPATIBLE_MODEL_NAME
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

    # APIエンドポイントURLを構築
    api_endpoint = f"{base_url}/chat/completions"

    # リクエストヘッダーを準備
    headers = {
        "Content-Type": "application/json"
    }

    # APIキーがある場合はヘッダーに追加
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # リクエストボディを準備
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    }

    # POSTリクエストを送信
    response = requests.post(api_endpoint, headers=headers, json=payload)

    # レスポンスを確認
    if response.status_code != 200:
        return f"Error: API request failed with status code {response.status_code}: {response.text}", 500

    # レスポンスからテキストを抽出
    response_data = response.json()
    translation = response_data["choices"][0]["message"]["content"]

    # remove start and end tags
    match = re.findall(r"<Start>(.*?)<End>", translation, re.DOTALL)
    if match:
        trans = match[-1]
    else:
        trans = ""

    # return translation
    return trans

# Run the Flask app
if __name__ == '__main__':
    app.run(host=listen_address, port=listen_port)
