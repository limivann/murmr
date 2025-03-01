from pydub import AudioSegment

def generate_challenges_audio(SOUND_DIR, PODCAST_DIR, OUTPUT_DIR):
  combined = (
    AudioSegment.from_file(f"{SOUND_DIR}/opening.mp3").fade_out(2000) + 
    AudioSegment.silent(duration=1000) +
    AudioSegment.from_file(f"{PODCAST_DIR}/podcast_intro.mp3") + 
    AudioSegment.from_file(f"{SOUND_DIR}/between.mp3")[:3000].fade_out(2000) + 
    AudioSegment.silent(duration=500) +
    AudioSegment.from_file(f"{PODCAST_DIR}/challenges.mp3") +
    AudioSegment.from_file(f"{SOUND_DIR}/ending.mp3").fade_out(1000)
  )
  combined.export(f"{OUTPUT_DIR}/combined_challenges.mp3", format="mp3")

def generate_news_audio(SOUND_DIR, PODCAST_DIR, OUTPUT_DIR):
  combined = (
    AudioSegment.from_file(f"{SOUND_DIR}/opening.mp3").fade_out(2000) + 
    AudioSegment.silent(duration=1000) +
    AudioSegment.from_file(f"{PODCAST_DIR}/news.mp3") +
    AudioSegment.from_file(f"{SOUND_DIR}/ending.mp3").fade_out(1000) 
  )
  combined.export(f"{OUTPUT_DIR}/combined_news.mp3", format="mp3")

def generate_therapy_audio(SOUND_DIR, PODCAST_DIR, OUTPUT_DIR, mood):
  opening = ""
  if mood == "happy":
    opening = AudioSegment.from_file(f"{SOUND_DIR}/happy_relax.mp3")
  elif mood == "sad":
    opening = AudioSegment.from_file(f"{SOUND_DIR}/sad_happy.mp3")
  else:
    opening = AudioSegment.from_file(f"{SOUND_DIR}/normal_calm.mp3")
  # opening = AudioSegment.from_file(f"{SOUND_DIR}/threapy_sound.mp3")
  opening = opening.apply_gain(-10)  # Reduce the volume of the opening sound
  podcast = AudioSegment.from_file(f"{PODCAST_DIR}/therapy.mp3")
  silence = AudioSegment.silent(duration=1000)  # 1 second silence before podcast

  total_duration = len(silence) + len(podcast)

  # Loop the opening sound to match the total duration
  looped_opening = (opening * (total_duration // len(opening) + 1))[:total_duration]

  # Combine silence and podcast
  main_audio = silence + podcast

  # Overlay the looped opening sound over the podcast
  combined = looped_opening.overlay(main_audio)

  # Export the final audio
  combined.export(f"{OUTPUT_DIR}/combined_therapy.mp3", format="mp3")
  
 