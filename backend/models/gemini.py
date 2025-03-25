import google.generativeai as genai
from config import GENAI_API_KEY
from models.rag import search_pinecone  # Import RAG for better context

# Configure Gemini API
genai.configure(api_key=GENAI_API_KEY)
llm = genai.GenerativeModel("gemini-2.0-flash")

def generate_response(query, grade=None, subject=None):
    """Generates a response using RAG to ensure accuracy and relevance."""
    
    # Retrieve relevant knowledge from Pinecone (RAG)
    retrieved_docs = search_pinecone(query, grade, subject, top_k=5)
    
    # If relevant content is found, use it in the prompt
    if retrieved_docs:
        context = "\n".join(retrieved_docs)
        prompt = f"Based on the following learning materials, answer this query accurately:\n\n{context}\n\nQuery: {query}"
    else:
        prompt = f"Explain this topic in detail: {query}"
    
    # Generate response using Gemini
    response = llm.generate_content(prompt)
    
    return response.text

def generate_exam(grade, subject, num_questions=5):
    """Generates an exam with structured questions based on retrieved content."""
    
    # Retrieve relevant content for the subject and grade
    retrieved_docs = search_pinecone(f"Exam questions for {subject} in grade {grade}", grade, subject, top_k=5)
    
    context = "\n".join(retrieved_docs) if retrieved_docs else ""
    
    prompt = f"""
    Generate {num_questions} exam questions for {subject} in Grade {grade}.
    Questions should be relevant and structured as multiple-choice and short-answer.
    Use the following learning materials if available:
    
    {context}
    """
    
    response = llm.generate_content(prompt)
    
    return response.text

def mark_exam(answers, grade, subject):
    """Evaluates student answers, assigns scores, and provides feedback."""
    
    prompt = f"""
    Evaluate the following student answers based on standard curriculum for Grade {grade} {subject}.
    Provide a detailed marking scheme, scores, and constructive feedback.
    
    Student Answers:
    {answers}
    """
    
    response = llm.generate_content(prompt)
    
    return response.text
