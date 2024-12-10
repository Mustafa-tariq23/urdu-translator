from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
from huggingface_hub import login
from pyngrok import ngrok, conf
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

# Set up Ngrok
# ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))

if os.getenv("RENDER"):
    public_url = "https://urdu-translator.onrender.com"
else:
    public_url = ngrok.connect(5000)
print(f"Public URL: {public_url}")


os.system("killall -9 ngrok")

conf.get_default().reuse_existing = True
try:
    tunnels = ngrok.get_tunnels()  # Get all active tunnels
    for tunnel in tunnels:
        ngrok.disconnect(tunnel.public_url)  # Disconnect each tunnel
except IndexError:
    pass  # if no tunnels exist, do nothing

public_url = ngrok.connect(5000)
print(f"ngrok URL: {public_url}")

# HuggingFace login
login(token=os.getenv("HF_TOKEN"))

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Initialize transcriber
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", device=0)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/translate', methods=['POST'])
def translate():
    try:
        # Check if 'audio' is in the request (handling audio files)
        if 'audio' in request.files:
            # Save the uploaded audio file
            file = request.files['audio']
            file.save("audio.wav")

            # Transcribe the audio file
            transcription = transcriber("audio.wav")['text']
        else:
            # Handle text input directly
            transcription = request.json.get('text')
            if not transcription:
                return jsonify({"error": "No text or audio provided for translation"}), 400

        # Send the transcription to Gemini for translation
        prompt = f"""Your role is to act as a translation expert. I will provide text in any language, and your task is to:
        1. Translate the text into both Original Urdu and Roman Urdu.
        2. If the text is already in Urdu, simply return the original text without modification.
        3. Ensure the response contains only the translations and nothing else.
        4. Don't return the 'original urdu' and 'roman urdu' with the response. Only return the translations.
        TEXT: '{transcription}'"""
        response = model.generate_content(prompt)

        # Check and format the response
        if response and hasattr(response, 'text'):
            translation = response.text
        else:
            translation = "Translation failed. No response received from Gemini API."

        # Print and return the response
        print("Backend Response:", {"transcription": transcription, "translation": translation})
        return jsonify({"transcription": transcription, "translation": translation})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

