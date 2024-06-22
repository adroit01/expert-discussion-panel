import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
import langchain
import requests

def google_genai_api_call(query: str):
    payload  = {'contents':[{"parts":[{"text":f"{query}"}]}]}
    response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={os.getenv('GOOGLE_API_KEY')}",
                             headers={"Content-Type":"application/json"},
                             json=payload)
    json_response = json.loads(response.text)
    return json_response

load_dotenv()
langchain.debug = True
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)

llm = ChatGoogleGenerativeAI(model="gemini-pro",convert_system_message_to_human=True)
response  = llm.invoke("Who is President of India")
print(response.content)

api_response = google_genai_api_call("Write 10 lines about gemini")
print(api_response)

