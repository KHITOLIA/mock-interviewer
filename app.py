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
from datetime import datetime


# Hello, my name is Tushar Khitoliya, and I am an AI-ML Engineer. I completed my B.Tech in Electrical and Electronics Engineering from the National Institute of Technology, Delhi.

# I have strong expertise in Python, machine learning, deep learning, NLP, and Generative AI tools like HuggingFace and LangChain vector databases and RAG frameworks . I have worked on projects including a Music Genre Classifier, Plant Disease Diagnosis system, and a medical chatbot using Retrieval-Augmented Generation.

# Professionally, I have trained corporate teams on AI and ML at Blogic Software Technology and mentored students at Coding Blocks and served as an AI-ML trainer in Chitkara University, Punjab . 

# I am passionate about building AI-driven solutions, solving real-world problems, and continuously learning. I would love to contribute my skills and grow with your organization. Thank you for your time.



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
# ---------------------------
# Interview Page
# ---------------------------
def interview_page():
    st.title("📊 Excel AI Interviewer")

    if st.session_state.index < len(questions):
        q = questions[st.session_state.index]
        ans = excel_qna[q]["answer"]
        topic = excel_qna[q]["topic"]

        # Show interviewer question only once
        if f"asked_{st.session_state.index}" not in st.session_state:
            st.session_state[f"asked_{st.session_state.index}"] = True
            st.subheader("🧑🏻‍💼 Interviewer:")
            type_effect(q)
            st.markdown(tts(q), unsafe_allow_html=True)

        # Candidate input
        user_input = st.text_area("💬 Your Answer:", value="", key=f"input_{st.session_state.index}")

        if st.button("Submit Answer", key=f"btn_{st.session_state.index}"):
            if user_input.strip() == "":
                st.warning("⚠️ Please enter your answer before submitting.")
            else:
                user_emb = embedding_model.embed_query(user_input)
                ans_emb = embedding_model.embed_query(ans)
                similarity = cosine_similarity([user_emb], [ans_emb])[0][0] * 100

                # Save correctness for final score (instead of showing now)
                if similarity > 80:
                    feedback = random.choice(positive_response)
                    st.session_state.summary.append({"topic": topic, "correct": True})
                else:
                    feedback = random.choice(negative_response)
                    st.session_state.summary.append({"topic": topic, "correct": False})

                # Show feedback only (no score here)
                type_effect(feedback)
                st.markdown(tts(feedback), unsafe_allow_html=True)
                time.sleep(3)

                # Next question
                st.session_state.index += 1
                st.rerun()

    else:
        # Final summary and score
        st.subheader("📌 Interview Summary")
        st.balloons()

        incorrect_topics = [s["topic"] for s in st.session_state.summary if not s["correct"]]

        if incorrect_topics:
            st.error("You should focus more on these topics:")
            for t in set(incorrect_topics):
                st.write(f"- {t}")
            st.markdown(tts("You should focus more on " + ", ".join(set(incorrect_topics))), unsafe_allow_html=True)
            sleep(5)
        else:
            st.success("🎉 Great job! You performed well in all topics.")
            st.markdown(tts("Great job! You performed well in all topics."), unsafe_allow_html=True)
            sleep(5)

        # Final score
        correct_count = sum(1 for s in st.session_state.summary if s["correct"])
        percent = int((correct_count / len(questions)) * 100)
        st.success(f"🏆 Your final score: {percent}%")
        st.markdown(tts(f"Your final score is {percent} percent."), unsafe_allow_html=True)
        sleep(5)
        
        # Final score
        correct_count = sum(1 for s in st.session_state.summary if s["correct"])
        percent = int((correct_count / len(questions)) * 100)

        # Save result to users.json
        users = load_users()
        username = st.session_state.username
        if "results" not in users[username]:
            users[username]["results"] = []

        users[username]["results"].append({
            "score": percent,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "weak_topics": list(set([s["topic"] for s in st.session_state.summary if not s["correct"]]))
        })
        save_users(users)

        # Reset session
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
