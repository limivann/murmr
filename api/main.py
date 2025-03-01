import os
import base64
import requests
from fastapi import FastAPI, HTTPException, Query, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from transformers import TokenClassificationPipeline, AutoModelForTokenClassification, AutoTokenizer
from transformers.pipelines import AggregationStrategy
import shutil
from pydantic import BaseModel
from google import genai
import utils
import pandas as pd
import json
from core.translate import translate
from core.tts import tts
from core.mix_and_dub import *
from core.filter_and_clean import clean_output
from core.news import *
from core.podcasts import *

# Your API key.
API_KEY = ""

SOUND_DIR = "./sounds"
PODCAST_DIR = "./podcasts"

client = None
async def lifespan(app: FastAPI):
    global client
    client = genai.Client(api_key=API_KEY)
    print("Initialized Google Cloud client")
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, 
    allow_credentials=True, 
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

def generate_speech(text: str, language_code: str, voice_name: str) -> str:
    """Call the Google Cloud Text-to-Speech REST API."""
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
        output_filename = "output.mp3"
        with open(output_filename, "wb") as out:
            out.write(base64.b64decode(audio_content))
        return output_filename
    else:
        raise HTTPException(status_code=response.status_code, detail=f"TTS API error: {response.text}")


@app.get("/text2speech")
def text_to_speech_endpoint(
    text: str = Query(..., description="Text to convert to speech"),
    language_code: str = Query("en-US", description="Language code for TTS"),
    voice_name: str = Query("en-US-Wavenet-D", description="Voice name for TTS")
):
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' parameter")
    
    audio_file = generate_speech(text, language_code, voice_name)
    return FileResponse(audio_file, media_type="audio/mp3")

@app.get("/")
def root():
    return {"message": "Hello World"}

UPLOAD_DIR  = "./uploads"
@app.post("/upload")
def upload(file: UploadFile = File(...)):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    try:
        contents = file.file.read()
        with open(UPLOAD_DIR + "/test.csv", 'wb') as f:
            f.write(contents)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='Something went wrong')
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}

### GEMINI for combining analysis, news, user_prompt and mood ###

# generate (challenges + healthcare solution) prompt based on analysis
# generate podcast for life story, for whatever the user is going through
def craft_podcast_intro(mood, date=""):
    """Generate a concise, engaging podcast intro based on the user's mood."""
    return utils.dedent(f"""
    Hey there! Welcome to your personal health check-in. I'm your host, and I'm glad you're here.
    
    If you're feeling {mood}, a little stuck, or just curious, you're in the right place. 
    Grab a tea, take a deep breath, and let's dive in!
    """)
    
def craft_challenges_prompt(analysis, user_prompt):
    """Generate a natural health challenge and solution segment."""
    return utils.dedent(f"""
    Based on the user's health insights:
    
    **Health Status:** {analysis}
    {f'**What They Feel:**{user_prompt}' if user_prompt else ""}
    
    Create a natural, engaging 30-second podcast segment that:
    - Identifies their key challenge.
    - Offers a **realistic**, **achievable** solution.
    - Sounds like a friendly radio host speaking, NOT a robotic AI. 
    - Uses real-life analogies, humor (if appropriate), and warm encouragement.
    - The target audience is only one user, so use "you" and "your" to address them.
    
    In the script, just output text without any speaker tags and music cues.
    """)
    
def craft_news_prompt(news, analysis):
    """Generate a radio-style health news segment."""
    return utils.dedent(f"""    
    Create a natural, engaging 30 seconds podcast segment that:
    - Keep it engaging, short, and easy to digest.  
    - Relate the news to everyday life.
    - End with a key takeaway or how the listener can benefit.
    - The target audience is only one user, so use "you" and "your" to address them.
    
    You can start with 
    Welcome to today's *Health Update*! 
    We've got something interesting to talk about: ...
    
    Based on user's analysis: \'{analysis}\'.You must pick a relevant news to talk about from below: {news}
        
    In the script, just output text without any speaker tags and music cues.
    """)

def craft_therapeutic_prompt(mood):
    """Generate a closing segment with supportive, human-like words."""
    return utils.dedent(f"""
    Generate a warm, supportive closing message for a 30 second podcast that:
    based on their mood which is {mood}

    - Craft a **warm, heartfelt message** for the listener.
    - Keep it short, but **deeply personal**.
    - Offer a **simple action** they can take today (breathing, movement, journaling).
    - Make them feel **seen, heard, and understood**.
    - The target audience is only one user, so use "you" and "your" to address them.
    
    You may start with: Before we wrap up, let's take a moment to reflect. 
    You've been feeling {mood}, and that's okay. We all go through ups and downs. 
    
    You may end with: Until next time, stay well, take care, and remember—you're doing better than you think. 
    In the script, just output text without any speaker tags and music cues.
    """)

class SummaryRequest(BaseModel):
    analysis: str
    user_prompt: str
    mood: str

csv_file = "health_news.csv"
@app.post("/gemini-podcast")
def generate_podcasts(request: SummaryRequest):
    if not request.analysis:
        raise HTTPException(status_code=400, detail="Missing 'analysis' parameter")
    if not request.user_prompt:
        raise HTTPException(status_code=400, detail="Missing 'user_prompt' parameter")
    if not request.mood:
        raise HTTPException(status_code=400, detail="Missing 'mood' parameter")
    
    # Generate 3 podcasts for the user 
    # 1. Challenges
    # 2. News Update
    # 3. therapathic words
    # Generate prompts for each podcast
    # today = utils.get_today_str()
    # print("today's date", today)
    news = get_health_news_from_csv(csv_file)
    
    podcast_intro = craft_podcast_intro(request.mood)
    challenges_prompt = craft_challenges_prompt(request.analysis, request.user_prompt)
    news_prompt = craft_news_prompt(news, request.analysis)
    therapeutic_prompt = craft_therapeutic_prompt(request.mood)
    
    challenges_response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=challenges_prompt
    )
    print("Generated challenges response")
    news_response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=news_prompt
    )
    print("Generated news response")
    therapeutic_response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=therapeutic_prompt
    )
    print("Generated therapeutic response")  
    return {"podcast_intro": podcast_intro, "challenges": challenges_response.text, "news": news_response.text, "therapeutic": therapeutic_response.text}

# Preprocess to generate health news for the user

@app.get("/health-news")
def generate_news():
    return get_health_news(csv_file)


music_cues_syntax = "### MUSIC CUE ###" 
# Clean podcast and add music cues to make it more natural, engaging, remove unncessary chars
def clean_podcast(podcast_intro, challenges, news, therapeutic):
    # Remove extra spaces and newlines
    podcast_intro = podcast_intro.strip().replace("\n", "")
    challenges = challenges.strip().replace("\n", "")
    news = news.strip().replace("\n", "")
    therapeutic = therapeutic.strip().replace("\n", "")
    
    return {"podcast_intro": podcast_intro, "challenges": challenges, "news": news, "therapeutic": therapeutic}

# main endpoint for generating podcasts

class GenerateRequest(BaseModel):
    user_prompt: str
    mood: str
    language: str

@app.post("/generate")
def generate(request: GenerateRequest):
    file = "./uploads/test.csv"
    # read csv file
    url = "http://127.0.0.1:8789/med-summarizer"
    health_data = {}
    health_data_df = pd.read_csv(file)
    for index, row in health_data_df.iterrows():
        if "type" in row and "value" in row:  # Check if both 'type' and 'value' columns exist
            key = row["type"]
            value = row["value"]
            health_data[key] = value
        else:
            print(f"Skipping row {index}!")
    health_data = utils.convert_to_int(health_data)
    payload = {"health_data": json.dumps(health_data)}
    headers = {
        "Content-Type": "application/json"
    }

    print("Analysing health data...")
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        health_analysis = data['analysis']
        print("Health data analysis are analysed")
        if not health_analysis:
            raise HTTPException(status_code=500, detail="No health analysis returned by medalpaca.")
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Medalpaca retrieve error: {response.text}")


    # Get analysis output using model
    # health_analysis = "The person has low physical activity levels as shown by his low daily energy consumption (1716 kcal) and water intake (709 ml), high body mass index (23.5981), low walking speed (2.34 m/s), running power (296 watts), VO2 max (46.64 ml/(kg·min)), number of steps taken (18 steps), stair descent speed (1.45 m/s), and distance cycled (0.003 km). He also had an irregular dietary pattern with missing meals and no record of having eaten any apples that day. His heart rate was abnormal, showing high average walking heart rates (125 bpm), high variability of heart rate (standard deviation of successive differences between normal RR intervals of 59 ms), high resting heart rate (56 bpm), and one event where his heart rate exceeded 100% of his maximum heart rate for more than five minutes (heart rate: 158 bpm; maximum heart rate: 133 bpm). He showed reduced sleep duration (goal: 8 hours) and poor oxygen saturation during sleep (0.99). Other negative findings included irregularities in respiration rate, which increased to 24–30 breaths per minute after exercise, six-minute walk test at only 500 meters, sedentarism (stand hour: 1 hour), and low active energy expenditure (1022 kcal). Positive findings include two flights climbed, good balance during standing (steadiness: 1.0), normal vitals except for elevated pulse oximetry reading (100%) recorded once when not wearing the Apple Watch, and low stress level based on one mindfulness session recorded that day."
    
    # Get other components
    user_prompt = request.user_prompt
    mood = request.mood
    language = request.language
    news_history = get_health_news_from_csv(csv_file)
    
    # Generate podcast segments
    print("Generating podcast content...")
    podcasts = generate_all_podcasts(health_analysis, user_prompt, mood, news_history)
    print("Podcast content are generated")
    podcast_intro = podcasts["podcast_intro"]
    challenges = podcasts["challenges"]
    news = podcasts["news"]
    therapeutic = podcasts["therapeutic"]
    
    # translate
    # TODO: Replace with podcasts
    podcast_intro_translated = translate(podcast_intro, language)
    challenges_translated = translate(challenges, language)
    news_translated = translate(news, language)

    therapeutic_translated = translate(therapeutic, language)
    print("Text translation completed")
    # filter and clean
    podcast_intro_translated = clean_output(podcast_intro_translated)
    podcast_intro_translated = podcast_intro_translated.strip().replace("\n", "")
    challenges_translated = clean_output(challenges_translated)
    challenges_translated = challenges_translated.strip().replace("\n", "")
    news_translated = clean_output(news_translated)
    news_translated = news_translated.strip().replace("\n", "")
    therapeutic_translated = clean_output(therapeutic_translated)
    therapeutic_translated = therapeutic_translated.strip().replace("\n", "")
    print("Text are cleaned up")
    
    # text to speech
    
    print("Generating audio file...")
    OUTPUT_FILE = f"{PODCAST_DIR}/podcast_intro.mp3"
    audio_file = tts(OUTPUT_FILE, podcast_intro_translated, language_code=language)
    OUTPUT_FILE = f"{PODCAST_DIR}/challenges.mp3"
    audio_file = tts(OUTPUT_FILE, challenges_translated, language_code=language)
    OUTPUT_FILE = f"{PODCAST_DIR}/news.mp3"
    audio_file = tts(OUTPUT_FILE, news_translated, language_code=language)
    OUTPUT_FILE = f"{PODCAST_DIR}/therapy.mp3"
    audio_file = tts(OUTPUT_FILE, therapeutic_translated, language_code=language)
    
    # mix and dub
    FINAL_OUTPUT_DIR = "../client/public/podcasts"
    if not os.path.exists(FINAL_OUTPUT_DIR):
        os.makedirs(FINAL_OUTPUT_DIR)
    print("Mixing and dubbing audio...")
    generate_challenges_audio(SOUND_DIR, PODCAST_DIR, FINAL_OUTPUT_DIR)
    print("Daily check-in audio are generated")
    generate_news_audio(SOUND_DIR, PODCAST_DIR, FINAL_OUTPUT_DIR)
    print("Personalized health news audio are generated")
    generate_therapy_audio(SOUND_DIR, PODCAST_DIR,FINAL_OUTPUT_DIR, mood)
    print("Therapy guide audio are generated")
    
    return {"success": "okie dokie"}

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
