import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME") 