from sentence_transformers import SentenceTransformer

embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def generate_embedding(text):
    return embed_model.encode(text).tolist()
