from dotenv import load_dotenv 
from pydantic import BaseModel 
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(model="llama3")

response = llm.invoke("What is the meaning of life?")
print(response.content)