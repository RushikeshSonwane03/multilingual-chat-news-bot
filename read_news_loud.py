# read_news_loud.py

from gtts import gTTS

def generate_audio(text, filepath, lang='hi'):
    tts = gTTS(text=text, lang=lang)
    tts.save(filepath)
    print("Audio Generated")
    
