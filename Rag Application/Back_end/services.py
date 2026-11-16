from google import genai
from dotenv import load_dotenv
import os
from pathlib import Path

from database import askQuestion
from langchain_core.prompts import ChatPromptTemplate

load_dotenv(Path(__file__).with_name(".env"))

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def create_prompt(question: str) -> str:

    chunks = askQuestion(question)

    context = ""

    for doc in chunks:
        context += doc.page_content + "\n\n"

    prompt_template = ChatPromptTemplate.from_template("""
        You are a helpful AI assistant.

        Answer the user's question using only the
        information provided in the context.

        If the answer is not available in the context,
        respond with:
        "I don't know based on the provided information."

        Context:
        {context}

        Question:
        {question}

        Answer:
    """)

    formatted_prompt = prompt_template.invoke({
        "context": context,
        "question": question
    })

    return formatted_prompt.to_string()


def findResponse(question: str) -> str:

    final_prompt = create_prompt(question)

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=final_prompt
    )

    return response.text