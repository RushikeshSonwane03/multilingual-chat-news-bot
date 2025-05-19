# app.py    

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_file
from chat_module import get_response
from news_module import fetch_top_news
from read_news_loud import generate_audio  # Your gTTS or audio function
from flask_session import Session
import uuid
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("GEMINI_API_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

DB_PATH = "db/chat_history.db"

SUPPORTED_LANGUAGES = {
    "en": "English", "hi": "Hindi", "mr": "Marathi", "ur": "Urdu",
    "ta": "Tamil", "te": "Telugu", "ml": "Malayalam", "sa": "Sanskrit"
}

SUPPORTED_TOPICS = {
     'top': 'top', 'business': 'business', 'crime': 'crime', 'domestic': 'domestic', 'education': 'education', 'entertainment': 'entertainment', 'environment': 'environment', 'food': 'food', 'health': 'health', 'lifestyle': 'lifestyle', 'politics': 'politics', 'science': 'science', 'sports': 'sports', 'technology': 'technology', 'tourism': 'tourism', 'world': 'world', 'other': 'other', 
    }

# ---------- Voice Input Handler ----------
def voice_input(transcript, language):
    print(transcript)
    return transcript

@app.route("/process_voice_input", methods=["POST"])
def process_voice_input():
    data = request.get_json()
    transcript = data.get("transcript", "")
    language = data.get("language", "en")

    input_text = voice_input(transcript, language)

    return jsonify({"input_text": input_text})

@app.route("/chat_voice_result")
def chat_voice_result():
    input_text = request.args.get("text", "")

    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    current_id = session["session_id"]
    messages = get_messages(current_id)
    history_ids = get_all_session_ids()

    return render_template("index.html", messages=messages, session_id=current_id,
                           user_input=input_text,
                           history_ids=history_ids, languages=SUPPORTED_LANGUAGES,
                           topics=SUPPORTED_TOPICS)


# ---------- Read Message Loud ----------
@app.route('/read_message_loud', methods=['POST'])
def read_message_loud():
    print("Calling : read_message_loud()")
    data = request.get_json()
    title = data.get('title', '')
    description = data.get('description', '')
    
    full_text = f"{title}. {description}"
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join("static/audio", filename)

    # Generate audio
    print("Calling : generate_audio()")
    generate_audio(full_text, filepath)

    # Return the audio file
    response = send_file(filepath, mimetype="audio/mpeg")

    # Optional: remove file after response
    @response.call_on_close
    def cleanup():
        os.remove(filepath)

    return response

# ---------- Read News Loud ----------
@app.route('/read_news_loud', methods=['POST'])
def read_news_loud():
    print("Calling : read_news_loud()")
    data = request.get_json()
    title = data.get('title', '')
    description = data.get('description', '')
    
    full_text = f"{title}. {description}"
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join("static/audio", filename)

    # Generate audio
    print("Calling : generate_audio()")
    generate_audio(full_text, filepath)

    # Return the audio file
    response = send_file(filepath, mimetype="audio/mpeg")

    # Optional: remove file after response
    @response.call_on_close
    def cleanup():
        os.remove(filepath)

    return response

# ---------- Database Setup ----------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

init_db()


# ---------- Routes ----------
@app.route("/", methods=["GET"])
def index():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    # Start a fresh session (new chat)
    current_id = session["session_id"]

    messages = get_messages(current_id)
    history_ids = get_all_session_ids()
    
    return render_template("index.html", messages=messages, session_id=current_id,
                           history_ids=history_ids, languages=SUPPORTED_LANGUAGES, 
                           topics=SUPPORTED_TOPICS)


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form["user_input"]
    session_id = session.get("session_id")

    save_message(session_id, "user", user_input)
    reply = get_response(user_input)
    save_message(session_id, "assistant", reply)

    return redirect(url_for("index"))

@app.route("/get_news", methods=["POST"])
def get_news():
    language = request.form.get("language", "hi")
    topic = request.form.get("topic", "top")

    print(language)
    print(topic)

    news_data = fetch_top_news(language=language, topic=topic)
    # print("Fetched News:", news_data)

    return jsonify(news_data)


@app.route("/load_chat/<chat_id>")
def load_chat(chat_id):
    session["session_id"] = chat_id
    return redirect(url_for("index"))


@app.route("/new_chat")
def new_chat():
    session["session_id"] = str(uuid.uuid4())
    return redirect(url_for("index"))


# ---------- DB Functions ----------
def save_message(session_id, role, content):
    current_timestamp = datetime.now()
    print(current_timestamp)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO chats (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                  (session_id, role, content, current_timestamp))
        conn.commit()


def get_messages(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT role, content FROM chats WHERE session_id = ?", (session_id,))
        return [{"role": row[0], "content": row[1]} for row in c.fetchall()]


def get_all_session_ids():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT DISTINCT session_id FROM chats")
        return [row[0] for row in c.fetchall()]


if __name__ == "__main__":
    app.run(debug=True)
