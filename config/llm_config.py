import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from langchain_community.llms.gpt4all import GPT4All
import google.generativeai as genai
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama

load_dotenv()
EMBEDDING_MODEL_PAGE_REQUEST_LIMIT = 16

#OpenAI GPT
llm_openai=ChatOpenAI(name=os.getenv("DEPLOYMENT_NAME"), model="gpt-3.5-turbo",temperature=0.0)
llm_for_summary=ChatOpenAI(name=os.getenv("DEPLOYMENT_NAME"), model="gpt-3.5-turbo",temperature=0.0)

embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

#Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm_gemini_pro = ChatGoogleGenerativeAI(model="gemini-pro",convert_system_message_to_human=True)

#llm for Sumamrization
#llm_for_summary = ChatGoogleGenerativeAI(model="gemini-pro")

#llama
callbacks = [StreamingStdOutCallbackHandler()]
#llm_llama_2_chat_7b_q4_0 = GPT4All(model="llama_7B_chat_q4_0_model_path",device="cpu",callbacks=callbacks,verbose=True)
meta_llm_llama3_8B_Instruct = Ollama(model="llama3")
llm_types = {
    "OpenAI-GPT-3.5 Turbo": llm_openai,
    "Meta-llama3-8B-Instruct": meta_llm_llama3_8B_Instruct,
    "Google's Gemini Pro": llm_gemini_pro,
    "human": "Human"
}
