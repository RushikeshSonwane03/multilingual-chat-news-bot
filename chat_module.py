# chat_module.py

from google import genai
import os
from dotenv import load_dotenv
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# System instruction
# system_instruction = (
#     "You are an AI Chatbot serving as an Assistant to the user. You will take input in multiple languages you will reply in the same language only.Be polite and give concise, to-the-point responses. Langauges are : (English, Hindi, Marathi, Tamil, Telugu, Malayalam, Urdu, Sanskrit)."
# )

system_instruction = (
    """
    You are a helpful multilingual assistant. Always reply in the language the user uses in their question. 
    If the user asks in Hindi, reply in Hindi. If they use English or any other language, respond in that language.
    Make sure to complete your response fully. Based on the inputs you generate the length of response, If response has to be long, make it long, else make it of appropriate lenght.
    """
)

# Configuration for responses
config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    max_output_tokens=2048,
    top_k=2,
    top_p=0.5,
    temperature=1.0,
    stop_sequences=['\n'],
    seed=42,
)
stream=True

# Content history (optional, can be moved to session if needed)
contents = []

def get_response(user_input: str) -> str:
    print("->",user_input)
    contents.append({'role': 'user', 'parts': [user_input]})
    print("->",contents)  
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_input,
            config=config,
        )
        reply = response.candidates[0].content.parts[0].text
        # contents.append({'role': 'model', 'parts': [reply]})
        contents.append({'role': 'model', 'parts': [contents]})
        return reply

    except Exception as e:
        return "माफ़ कीजिए, मुझे आपका संदेश समझ नहीं आया। कृपया फिर से प्रयास करें।"
