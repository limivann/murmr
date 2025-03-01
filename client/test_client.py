import requests

def test_translate_endpoint():
    base_url = "http://127.0.0.1:8000"
    
    # Prompt user for text and translation direction.
    text = input("Enter text to translate: ")
    direction = input("Enter translation direction (en_to_zh or zh_to_en): ")

    # Build the URL and parameters.
    url = f"{base_url}/translate"
    params = {
        "text": text,
        "direction": direction
    }
    
    # Send GET request to the /translate endpoint.
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print("\nTranslation Result:")
        print("Translated Text:", data.get("translatedText"))
        # No audio file is returned by /translate endpoint now.
    else:
        print("Error:", response.status_code, response.text)

def test_text2speech_endpoint():
    base_url = "http://127.0.0.1:8000"
    
    # Prompt user for text for TTS.
    text = input("Enter text for text-to-speech: ")
    language_code = input("Enter language code (default en-US): ") or "en-US"
    voice_name = input("Enter voice name (default en-US-Wavenet-D): ") or "en-US-Wavenet-D"

    # Build the URL and parameters.
    url = f"{base_url}/text2speech"
    params = {
        "text": text,
        "language_code": language_code,
        "voice_name": voice_name
    }
    
    # Send GET request to the /text2speech endpoint.
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # The response will be an MP3 file.
        output_filename = "output_text2speech.mp3"
        with open(output_filename, "wb") as f:
            f.write(response.content)
        print(f"Audio content saved as {output_filename}")
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    print("Choose a test option:")
    print("1. Translate text")
    print("2. Text-to-speech conversion")
    choice = input("Enter 1 or 2: ").strip()
    
    if choice == "1":
        test_translate_endpoint()
    elif choice == "2":
        test_text2speech_endpoint()
    else:
        print("Invalid choice.")
