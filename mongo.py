import requests
# import streamlit as st
# import openai as OpenAI
# st.title("SEERAH BOT")
import pymongo
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 
mongo_key=os.getenv("mongo_key")
mongo_pass=os.getenv("mongo_pass")
from urllib.parse import quote_plus

username = quote_plus(mongo_key)
password = quote_plus(mongo_pass)
MONGO_URI = 'mongodb+srv://' + username + ':' + password + '@datacluster.hjhs3xb.mongodb.net/'
client = pymongo.MongoClient(MONGO_URI)
db = client.books
collection = db.books

# db = client.sample_mflix
# collection = db.movies
hf_token = os.getenv("hf_token") 

embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

def generate_embedding(text: str) -> list[float]:

    response = requests.post(
        embedding_url,
        headers={"Authorization": f"Bearer {hf_token}"},
        json={"inputs": text})

    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")

    return response.json()
# getT=generate_embedding("MongoDB is awesome")
# print(len(getT))
for doc in collection.find():
	doc['plot_embedding_hf'] = generate_embedding(doc['text'])
	collection.replace_one({'_id': doc['_id']}, doc)

query = "Seerah of Prophet Muhammad pbuh"

results = collection.aggregate([
  {"$vectorSearch": {
    "queryVector": generate_embedding(query),
    "path": "plot_embedding_hf",
    "numCandidates": 100,
    "limit": 4,
    "index": "PlotSemanticSearchs",
      }}
])
print("Results",results)
for document in results:
    print(f'Book Name: {document["title"]},\Book Plot: {document["text"]}\n')