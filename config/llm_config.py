import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from langchain_community.llms.gpt4all import GPT4All
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaLLM
from langchain_anthropic import ChatAnthropic

load_dotenv()
EMBEDDING_MODEL_PAGE_REQUEST_LIMIT = 16

#OpenAI GPT
llm_openai=ChatOpenAI(model="gpt-3.5-turbo",temperature=0.7)
llm_openai_4o_mini=ChatOpenAI(model="gpt-4o-mini-2024-07-18",temperature=0.7)
llm_openai_4o=ChatOpenAI(model="gpt-4o",temperature=0.7)
llm_openai_4_1_mini=ChatOpenAI(model="gpt-4.1-mini",temperature=0.7)

embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

#Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm_gemini_pro = ChatGoogleGenerativeAI(model="gemini-pro",convert_system_message_to_human=True)
llm_gemini_2_0_flash = ChatGoogleGenerativeAI(model="gemini-2.0-flash",convert_system_message_to_human=True)
llm_gemini_2_5_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash",convert_system_message_to_human=True)


#llama
#callbacks = [StreamingStdOutCallbackHandler()]
#llm_llama_2_chat_7b_q4_0 = GPT4All(model="llama_7B_chat_q4_0_model_path",device="cpu",callbacks=callbacks,verbose=True)
meta_llm_llama3_8B_Instruct = OllamaLLM(model="llama3")

#deepseek
llm_deepseek_r1_1_5b = OllamaLLM(model="deepseek-r1:1.5b")
llm_deepseek_r1_8b = OllamaLLM(model="deepseek-r1:8b")

#Anthropic Claude
llm_claude_sonnet = ChatAnthropic(model="claude-sonnet-4-6",temperature=0.7)
llm_claude_haiku = ChatAnthropic(model="claude-haiku-4-5-20251001",temperature=0.7)

#llm for Sumamrization
#llm_for_summary = ChatGoogleGenerativeAI(model="gemini-2.0-flash",convert_system_message_to_human=True)
llm_for_summary = llm_claude_sonnet

llm_types = {
    "OpenAI-GPT-3.5 Turbo": llm_openai,
    "OpenAI-GPT-4o-mini" : llm_openai_4o_mini,
    "OpenAI-GPT-4o": llm_openai_4o,
    "OpenAI-GPT-4.1-mini": llm_openai_4_1_mini,
    "Meta-llama3-8B-Instruct": meta_llm_llama3_8B_Instruct,
    "Google's Gemini Pro": llm_gemini_pro,
    "Google's Gemini 2.0 Flash": llm_gemini_2_0_flash,
    "Google's Gemini 2.5 Flash": llm_gemini_2_5_flash,
    "Anthropic Claude Sonnet 4.6": llm_claude_sonnet,
    "Anthropic Claude Haiku 4.5": llm_claude_haiku,
    "Deepseek r1 1.5b": llm_deepseek_r1_1_5b,
    "Deepseek r1 8b": llm_deepseek_r1_8b,
    "human": "Human"
}
