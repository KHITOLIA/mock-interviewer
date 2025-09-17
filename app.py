import streamlit as st
import json
import os
import random
import warnings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from time import sleep
from gtts import gTTS
import base64
import tempfile
import time

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Excel AI Interviewer", layout="centered")

# ---------------------------
# File to store users
# ---------------------------
USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

# ---------------------------
# Embedding model (cached)
# ---------------------------
@st.cache_resource
def load_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

embedding_model = load_model()

# ---------------------------
# Q&A Bank
# ---------------------------
excel_qna = {
    "How do you remove duplicate values from a column in Excel?": {
        "answer": "Select the column > Data tab > Remove Duplicates.",
        "topic": "Data Cleaning"
    },
    "What does VLOOKUP do in Excel?": {
        "answer": "VLOOKUP searches for a value in the first column of a range and returns a value in the same row from another column.",
        "topic": "Lookup & Reference"
    }
}
questions = list(excel_qna.keys())

positive_response = [
    "That’s a good answer, you explained it well.",
    "Correct, your response is relevant to the question.",
    "Good point, that’s exactly what I was expecting.",
]
negative_response = [
    "I appreciate your effort, but that doesn’t fully address the question.",
    "Good attempt, but your answer is slightly off.",
    "You’re on the right track, but something important is missing.",
]

# ---------------------------
# Session State
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "index" not in st.session_state:
    st.session_state.index = 0
if "summary" not in st.session_state:
    st.session_state.summary = []

# ---------------------------
# Text to Speech
# ---------------------------
def tts(text):
    """Convert text to speech and return as HTML audio (autoplay hidden)."""
    tts_audio = gTTS(text)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts_audio.save(tmp.name)

    with open(tmp.name, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    audio_html = f"""
        <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    return audio_html

# ---------------------------
# Typing Effect
# ---------------------------
def type_effect(text, delay=0.03):
    placeholder = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(delay)
    return

# ---------------------------
# Register Page
# ---------------------------
def register_page():
    st.title("📝 Register as New User")
    new_user = st.text_input("Choose a Username")
    new_pass = st.text_input("Choose a Password", type="password")

    if st.button("Register"):
        users = load_users()
        if new_user in users:
            st.error("⚠️ Username already exists. Try another.")
        elif new_user == "" or new_pass == "":
            st.warning("⚠️ Please enter both username and password.")
        else:
            users[new_user] = {"password": new_pass}
            save_users(users)
            st.success("✅ Registration successful! Please login now.")
            st.session_state.page = "login"
            st.rerun()

    st.info("👉 Already registered? Go back to login.")
    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()

# ---------------------------
# Login Page
# ---------------------------
def login_page():
    st.title("🔐 Login to Excel AI Interviewer")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        if username in users and users[username]["password"] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.info("👉 New here? Click below to register.")
    if st.button("Go to Register"):
        st.session_state.page = "register"
        st.rerun()

# ---------------------------
# Interview Page
# ---------------------------
def interview_page():
    st.title("📊 Excel AI Interviewer")

    if st.session_state.index < len(questions):
        q = questions[st.session_state.index]
        ans = excel_qna[q]["answer"]
        topic = excel_qna[q]["topic"]

        # Show interviewer question with typing effect
        st.subheader("🧑🏻‍💼 Interviewer:")
        type_effect(q)
        st.markdown(tts(q), unsafe_allow_html=True)

        # Candidate input (always blank after rerun)
        user_input = st.text_area("💬 Your Answer:", value="", key=f"input_{st.session_state.index}")

        if st.button("Submit Answer", key=f"btn_{st.session_state.index}"):
            if user_input.strip() == "":
                st.warning("⚠️ Please enter your answer before submitting.")
            else:
                user_emb = embedding_model.embed_query(user_input)
                ans_emb = embedding_model.embed_query(ans)
                similarity = cosine_similarity([user_emb], [ans_emb])[0][0] * 100

                # Feedback with typing effect
                if similarity > 80:
                    feedback = random.choice(positive_response)
                    type_effect("✅ " + feedback)
                    st.markdown(tts(feedback), unsafe_allow_html=True)
                    time.sleep(4)
                    st.write(f"**Your Score:** {int(np.round(similarity))}")
                else:
                    feedback = random.choice(negative_response)
                    type_effect("❌ " + feedback)
                    st.markdown(tts(feedback), unsafe_allow_html=True)
                    time.sleep(4)
                    st.session_state.summary.append(topic)

                # Move to next question
                st.session_state.index += 1
                if st.session_state.index < len(questions):
                    next_q = questions[st.session_state.index]
                    st.markdown(tts("Next Question: " + next_q), unsafe_allow_html=True)

                st.rerun()

    else:
        # Final summary and score
        st.subheader("📌 Interview Summary")
        st.balloons()

        if st.session_state.summary:
            st.error("You should focus more on these topics:")
            for t in set(st.session_state.summary):
                st.write(f"- {t}")
            st.markdown(tts("You should focus more on " + ", ".join(set(st.session_state.summary))), unsafe_allow_html=True)
            sleep(5)  # wait for summary voice
        else:
            st.success("🎉 Great job! You performed well in all topics.")
            st.markdown(tts("Great job! You performed well in all topics."), unsafe_allow_html=True)
            sleep(5)  # wait for summary voice

        # Final score voice
        final_score = len(questions) - len(st.session_state.summary)
        percent = int((final_score / len(questions)) * 100)
        st.markdown(tts(f"Your final score is {percent} percent."), unsafe_allow_html=True)
        sleep(5)

        # Reset session and go back to login
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.index = 0
        st.session_state.summary = []
        st.session_state.page = "login"
        st.rerun()

# ---------------------------
# Main Controller
# ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if not st.session_state.authenticated:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()
else:
    interview_page()
