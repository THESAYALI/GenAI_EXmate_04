# database.py

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv(Path(__file__).with_name(".env"))

API_KEY = os.getenv("GEMINI_API_KEY")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=API_KEY
)

vector_store = Chroma(
    collection_name="myCollection",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)


def addData(data: list):
    vector_store.add_texts(
        texts=data
    )
    print("Data stored successfully!")


def getData():
    data = vector_store.get()
    return data


def askQuestion(askedQuery: str):
    chunks = vector_store.similarity_search(
        query=askedQuery,
        k=2
    )
    return chunks