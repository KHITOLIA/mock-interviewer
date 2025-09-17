import random
from rich import print
import warnings
warnings.filterwarnings("ignore")
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from langchain_ollama import OllamaLLM
llm = OllamaLLM(model="wizardlm2", temperature=0, max_token=512)
model_name = 'sentence-transformers/all-mpnet-base-v2'
embedding_model = HuggingFaceEmbeddings(model_name = model_name)
questions = {
    'question1': 'what is the difference between list and tuple in python?',
    'question2' : 'how is the list data structure is different from tuples? '
}    
# positive_response = [
#     "That’s a good answer, you explained it well.",
# "Correct, your response is relevant to the question.",
# "Good point, that’s exactly what I was expecting.",
# "Yes, that’s the right direction.",
# "Your explanation makes sense, let’s move ahead.",
# "Well done, you addressed the question properly.",
# "That’s relevant, let me ask you a related question.",
# "You’re correct, now can you go a bit deeper?",
# "Nice explanation, it shows you understand the topic.",
# "Good, that’s aligned with the expected answer."
# ]

# negative_response = ["I appreciate your effort, but that doesn’t fully address the question. Would you like to try again?",
# "That’s an interesting perspective, though it’s not exactly what I was looking for. Let me guide you a bit.",
# "Good attempt, but your answer is slightly off. Maybe think about it from another angle.",
# "You’re on the right track, but something important is missing. Can you expand on it?",
# "Thanks for sharing, though it doesn’t quite match the question. Shall I rephrase it for you?",
# "Not a bad try, but let’s refine your answer a little more.",
# "I see where you’re going, but that’s not fully correct. Want me to give a small hint?",
# "That’s a thoughtful response, but not entirely relevant. Let’s revisit the question together.",
# "Nice attempt, though the answer isn’t complete. Can you think of another example?",
# "Good try, but let’s adjust the focus a bit to match the question."]
score = 0
for _, ques in questions.items():
    print(f"[bold blue]Interviewer:[/bold blue] : {ques}")
    user_input = input("give me your response : ")
    user_input_vector = embedding_model.embed_query(user_input)

    prompt = f"Answer the following question in 2 lines:\n{ques}"
    llm_response = llm.generate([prompt])
    llm_response_vector = embedding_model.embed_query(llm_response.generations[0][0].text)
    print(f"LLm_answer : {llm_response.generations[0][0].text}")

    similarity = cosine_similarity([llm_response_vector], [user_input_vector])[0][0]*100
    print(f"similar answer : {similarity:.2f}%")

    if similarity > 80:
        feedback_prompt = f"""
        You are an AI interviewer with a mix of professionalism, encouragement, and a touch of wit.  
        Since the answer is relevant and mostly correct, generate a short and engaging response.  
        - Be polite but confident.  
        - Add appreciation.  
        - You can be slightly humorous or sarcastic in a *positive* way, e.g., "Finally, someone who knows their stuff!" or "Not bad, you actually read the Python docs, huh?".  
        - Keep it under 1 sentences and always generate a different response every time .  
        """
        result = llm.generate([feedback_prompt])
        score = score + 1
        print(f"[bold green]Interviewer:[/bold green] {result.generations[0][0].text}")

    else:
        feedback_prompt = f"""
        You are an AI interviewer with a polite but witty personality. 
        The answer is not correct or relevant. Generate a short, constructive but slightly witty/sarcastic response.  
        - Be gentle so the candidate doesn’t feel bad.  
        - Encourage them to rethink, e.g., "Interesting… but not the Python I was asking about." or "Nice try, but you just unlocked the wrong door with the right key shape."  
        - Suggest politely that they try again or think differently.  
        - Keep it under 1 sentences and always generate a different response every time .  
        """
        result = llm.generate([feedback_prompt])
        print(f"[bold red]Interviewer:[/bold red] {result.generations[0][0].text}")
print(score)

