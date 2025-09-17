import pyttsx3
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voices', id(voices[0]))
engine.setProperty('rate', 150)

def tts(text):
    engine.say(text)
    engine.runAndWait()

# tts("I am sumit gandu. Your personal AI interviewer. I will ask you a series of questions to help you prepare for your upcoming interview. Let's get started!")
