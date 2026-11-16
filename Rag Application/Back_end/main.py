from fastapi import FastAPI
from pydantic import BaseModel

from database import addData, getData
from services import findResponse

app = FastAPI(title="RAG Application")

class DocumentInput(BaseModel):
    documents: list[str]

class ChatInput(BaseModel):
    prompt: str


@app.get("/")
def home():
    return "Welcome to RAG Application!"


@app.post("/collection")
def storeData(data: DocumentInput):
    addData(data.documents)
    return {"message": "Documents stored successfully!"}


@app.get("/collection")
def getCollectionData():
    return getData()


@app.post("/chat")
def getResponse(query: ChatInput):
    response = findResponse(query.prompt)
    return {"response": response}