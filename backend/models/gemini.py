import google.generativeai as genai
from config import GENAI_API_KEY

genai.configure(api_key=GENAI_API_KEY)
llm = genai.GenerativeModel("gemini-2.0-flash")

def generate_response(context):
    prompt = f"Explain this topic: {context}"
    return llm.generate_content(prompt).text
