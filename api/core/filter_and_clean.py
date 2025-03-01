from google import genai
import re

API_KEY = ""

client = genai.Client(api_key=API_KEY)

def clean_output(text):
    """
    Enhances the given text to sound more natural and conversational, 
    incorporating fillers like 'uhm', 'ahh' to mimic real speech patterns.
    """
    prompt = f"""
    Rewrite the following text to sound natural, like spoken dialogue in a podcast.
    - Add natural pauses and hesitations (like "uhm", "ahh").
    - Remove any non-dialogue elements (like asterisks, brackets, stage directions, or formatting markers).
    - Keep it fluid and conversational.
    It must be a dialogue within 20 seconds.
    Original text:
    {text}

    More natural version:
    """

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    # Extract text and clean it
    cleaned_text = response.text.strip()
    cleaned_text = re.sub(r"[\*\[\]{}<>]", "", cleaned_text)  # Removes *, [], {}, <>
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)  # Ensures clean spacing
    
    return cleaned_text