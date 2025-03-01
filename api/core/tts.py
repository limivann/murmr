import requests
from fastapi import HTTPException
import base64

API_KEY = ""

def generate_speech(output_file, text, language_code, voice_name):
  url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={API_KEY}"
  payload = {
    "input": {"text": text},
    "voice": {
      "languageCode": language_code,
      "name": voice_name
    },
    "audioConfig": {"audioEncoding": "MP3"}
  }
  response = requests.post(url, json=payload)
  if response.status_code == 200:
    data = response.json()
    audio_content = data.get("audioContent")
    if not audio_content:
      raise HTTPException(status_code=500, detail="No audio content returned by TTS API.")
    with open(output_file, "wb") as out:
      out.write(base64.b64decode(audio_content))
    return output_file
  else:
    raise HTTPException(status_code=response.status_code, detail=f"TTS API error: {response.text}")
  
def tts(output_file, text, language_code="en-US", voice_name="en-US-Chirp3-HD-Kore"):
  audio_file = generate_speech(output_file, text, language_code, voice_name)
  return audio_file


