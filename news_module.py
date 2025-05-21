# news_module.py

import requests
import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

NEWS_API_URL = "https://newsdata.io/api/1/news?apikey=" + NEWS_API_KEY


def translate_text(text, target_lang):
    try:
        # if target_lang == 'en' or not text:   # Excuse translation for English(Original Language.)
        if not text:   # Translate to the selected Language
            return text

        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        print(f"Translation failed for text: {text} | Error: {e}")
        return text  # fallback to original


def fetch_top_news(language='en', topic=None):
    try:
        # Build API parameters for category and country
        if not topic:
            topic = "top"  # default to 'top' if no topic is provided
        
        params = f"&category={topic}&country=in"

        # Make the API call
        res = requests.get(NEWS_API_URL + params)
        data = res.json()

        if data.get("status") != "success":
            print("API Error or bad request:", data)
            return []

        articles = data.get("results", [])[:5]  # Fetch top n news only

        news_list = []
        print("translating")
        for article in articles:
            title = article.get("title", "No Title")
            desc = article.get("description", "No Description Available")

            translated_title = translate_text(title, language)
            translated_desc = translate_text(desc, language)

            news_list.append({
                "title": translated_title,
                "description": translated_desc,
                "url": article.get("link", "#"),
                "image_url": article.get("image_url", None)
            })
        print("Done Translation")


        return news_list

    except Exception as e:
        print("Error fetching news:", e)
        return []


