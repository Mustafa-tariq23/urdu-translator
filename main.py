# Install required packages
# !pip install flask-cors
# !pip install pyngrok
# !pip install google-generativeai
# !pip install transformers
# !pip install huggingface-hub

# Import necessary libraries
from flask import Flask, request, jsonify
from flask_cors import CORS  # For handling CORS
from transformers import pipeline
from huggingface_hub import login
from pyngrok import ngrok, conf
import google.generativeai as genai
import os

# Set up Ngrok
ngrok.set_auth_token("2puHmwrbAwbjQZxsB4tNvueD5Dz_5nwZ6mPTf7pkSJsswxUMh")  # Replace with your actual Ngrok token

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
login(token="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")

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Initialize transcriber
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")

# Configure Gemini API
genai.configure(api_key="AIzaSyAcfbS0e_pWxRY-9_NMWjHlqXy64djI6Sc")  # Replace with your actual Gemini API key
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/translate', methods=['POST'])
def translate_audio():
    try:
        # Save the uploaded audio file
        file = request.files['audio']
        file.save("audio.wav")

        # Transcribe the audio file
        transcription = transcriber("audio.wav")['text']

        # Send the transcription to Gemini for translation
        prompt = f"""Your role is to act as a translation expert. I will provide text in any language, and your task is to:
        1. Translate the text into both Original Urdu and Roman Urdu.
        2. If the text is already in Urdu, simply return the original text without modification.
        3. Ensure the response contains only the translations and nothing else.
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
    app.run()
