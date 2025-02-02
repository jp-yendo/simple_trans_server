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

app = Flask(__name__)
@app.route('/translate', methods=['get'])

def translate():
    lang_from = request.args.get('from')
    lang_to = request.args.get('to')
    content = request.args.get('text')

    chat_session = model.start_chat(history=[])

    message = """You are a professional,authentic translation engine,only returns translations.\n
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
Translate the content to %s into %s:\n
\n
<Start>%s<End>""" % (lang_from, lang_to, content)

    response = chat_session.send_message(message)

    trans = re.sub(r"<Start>|<End>", "", response.text)

    return trans

if __name__ == '__main__':
    app.run(host=listen_address, port=listen_port)
