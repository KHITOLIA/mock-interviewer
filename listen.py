import speech_recognition as sr
from googletrans import Translator
from speak import tts

# lIsten.py
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("listening...")
        r.pause_threshold = 1
        audio = r.listen(source, 0, 15)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-en')
        tts(f"User said: {query}")
        return query
    except Exception as e:
        tts("Sorry, I could not understand the audio.")
        return None
    
# listen()    