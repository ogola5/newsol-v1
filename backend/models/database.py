from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["education_ai"]

def save_user_data(user_id, text, response):
    db.history.insert_one({"user_id": user_id, "query": text, "response": response})
