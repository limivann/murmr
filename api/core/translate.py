import requests
from fastapi import HTTPException

API_KEY = ""

def get_translation(text, target_language):
  """Call the Google Cloud Translation REST API."""
  url = f"https://translation.googleapis.com/language/translate/v2?key={API_KEY}"
  payload = {
    "q": text,
    "target": target_language
  }
  response = requests.post(url, json=payload)
  if response.status_code == 200:
    data = response.json()
    try:
      translated_text = data["data"]["translations"][0]["translatedText"]
    except (KeyError, IndexError):
      raise HTTPException(status_code=500, detail="Unexpected response structure from Translation API.")
    return translated_text
  else:
    raise HTTPException(status_code=response.status_code, detail=f"Translation API error: {response.text}")

def translate(text, target):
  if (target == "en"):
    return text
  
  # Translate to Chinese
  translated_text = get_translation(text, "zh")
  return translated_text
  
  