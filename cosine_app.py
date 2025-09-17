# from rich import print
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from sklearn.metrics.pairwise import cosine_similarity
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import random
from speak import tts
from listen import listen


model_name = 'sentence-transformers/all-mpnet-base-v2'

embedding_model = HuggingFaceEmbeddings(model_name = model_name)

positive_response = [
    "That’s a good answer, you explained it well.",
"Correct, your response is relevant to the question.",
"Good point, that’s exactly what I was expecting.",
"Yes, that’s the right direction.",
"Your explanation makes sense, let’s move ahead.",
"Well done, you addressed the question properly.",
"That’s relevant, let me ask you a related question.",
"You’re correct, now can you go a bit deeper?",
"Nice explanation, it shows you understand the topic.",
"Good, that’s aligned with the expected answer."
]

negative_response = ["I appreciate your effort, but that doesn’t fully address the question. Would you like to try again?",
"That’s an interesting perspective, though it’s not exactly what I was looking for. Let me guide you a bit.",
"Good attempt, but your answer is slightly off. Maybe think about it from another angle.",
"You’re on the right track, but something important is missing. Can you expand on it?",
"Thanks for sharing, though it doesn’t quite match the question. Shall I rephrase it for you?",
"Not a bad try, but let’s refine your answer a little more.",
"I see where you’re going, but that’s not fully correct. Want me to give a small hint?",
"That’s a thoughtful response, but not entirely relevant. Let’s revisit the question together.",
"Nice attempt, though the answer isn’t complete. Can you think of another example?",
"Good try, but let’s adjust the focus a bit to match the question."]

excel_qna = {
    # "What is the shortcut to create a new worksheet in Excel?": {
    #     "answer": "The shortcut is Shift + F11.",
    #     "topic": "Shortcuts"
    # }
    # "How do you freeze the top row in Excel?": {
    #     "answer": "Go to the View tab > Freeze Panes > Freeze Top Row.",
    #     "topic": "Data Navigation"
    # },
    # "What is the function to calculate the average in Excel?": {
    #     "answer": "The function is =AVERAGE(range).",
    #     "topic": "Functions"
    # },
    "How do you remove duplicate values from a column in Excel?": {
        "answer": "Select the column > Data tab > Remove Duplicates.",
        "topic": "Data Cleaning"
    },
    "What does VLOOKUP do in Excel?": {
        "answer": "VLOOKUP searches for a value in the first column of a range and returns a value in the same row from another column.",
        "topic": "Lookup & Reference"
    }
}

summary = []

print("Hello! and Welcome to this AI-powered Excel assessment. " \
"I am your AI interviewer, designed to evaluate your knowledge and skills in Microsoft Excel. " \
"During this session, I will ask you questions covering various topics such as formulas and functions, data analysis, data cleaning, shortcuts, and lookup & reference techniques.")

for question , value in excel_qna.items():
    print(f"[bold blue]Interviewer:[/bold blue] : {question}")
    # tts(question)


    # print(f"[bold blue]Interviewer:[/bold blue] : Speak up ypur answer  ")
    # user_input = listen()
    user_input = input("enter your answer ? ")
    user_embedding = embedding_model.embed_query(user_input)

    answer_embedding = embedding_model.embed_query(value['answer'])
    similarity = cosine_similarity([user_embedding], [answer_embedding])[0][0]*100

    if similarity>80:
        print(f"[bold green]Interviewer:[/bold green] {random.choice(positive_response)}")
        print(f"[bold green]Your score:[/bold green] {int(np.round(similarity))}")

    else:
        print(f"[bold red]Interviewer:[/bold red] {random.choice(negative_response)}")
        summary.append(value['topic']) 
if summary != []:
    print(f"[bold red]Interviewer:[/bold red] Try to take your commands on these topics carefully...")
    for topics in summary:
        print(topics)
