from google import genai
import utils

API_KEY = ""

client = genai.Client(api_key=API_KEY)
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
    
    Create a natural, engaging 20-second podcast segment that:
    - Identifies their key challenge.
    - Offers a **realistic**, **achievable** solution.
    - Sounds like a friendly radio host speaking, NOT a robotic AI. 
    - Uses real-life analogies, humor (if appropriate), and warm encouragement.
    - The target audience is only one user, so use "you" and "your" to address them.
    It must be a 20 second podcast.
    In the script, just output text without any speaker tags and music cues.
    """)
    
def craft_news_prompt(news, analysis):
    """Generate a radio-style health news segment."""
    return utils.dedent(f"""    
    Create a natural, engaging 20 seconds podcast for a radio-style health news segment. that:
    - Keep it engaging, short, and easy to digest.  
    - Relate the news to everyday life.
    - End with a key takeaway or how the listener can benefit.
    - The target audience is only one user, so use "you" and "your" to address them.
    
    You can start with 
    Welcome to today's *News Update* on health! 
    We've got something interesting to talk about: ...
    
    Based on user's analysis: \'{analysis}\'.You must pick a relevant news to talk about from below: {news}
    It must be a 20 second podcast.    
    In the script, just output text without any speaker tags and music cues.
    """)

def craft_therapeutic_prompt(mood):
    """Generate a closing segment with supportive, human-like words."""
    return utils.dedent(f"""
    Generate a warm, supportive closing message for a 20 second podcast that:
    based on their mood which is {mood}

    - Craft a **warm, heartfelt message** for the listener.
    - Keep it short, but **deeply personal**.
    - Offer a **simple action** they can take today (breathing, movement, journaling).
    - Make them feel **seen, heard, and understood**.
    - The target audience is only one user, so use "you" and "your" to address them.
    
    You may start with: Before we wrap up, let's take a moment to reflect. 
    You've been feeling {mood}, and that's okay. We all go through ups and downs. 
    It must be a 20 second podcast.
    You may end with: Until next time, stay well, take care, and remember—you're doing better than you think. 
    In the script, just output text without any speaker tags and music cues.
    """)

def generate_all_podcasts(analysis, user_prompt, mood, news):
    # Generate 3 podcasts for the user 
    # 1. Challenges
    # 2. News Update
    # 3. therapathic words
    # Generate prompts for each podcast
    # today = utils.get_today_str()
    # print("today's date", today)
    
    podcast_intro = craft_podcast_intro(mood)
    challenges_prompt = craft_challenges_prompt(analysis, user_prompt)
    news_prompt = craft_news_prompt(news, analysis)
    therapeutic_prompt = craft_therapeutic_prompt(mood)
    
    challenges_response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=challenges_prompt
    )
    print("Daily check-in content are generated")
    news_response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=news_prompt
    )
    print("Personalized health news are generated")
    therapeutic_response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=therapeutic_prompt
    )
    print("Therapy guide content are generated")  
    return {"podcast_intro": podcast_intro, "challenges": challenges_response.text, "news": news_response.text, "therapeutic": therapeutic_response.text}