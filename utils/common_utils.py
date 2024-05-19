import yaml
from langchain.agents.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from pypdf import PdfReader
from langchain.vectorstores.chroma import Chroma
import config.llm_config as config
import chromadb

def is_pdf(file_path) ->bool:
    try:
        reader = PdfReader(file_path)
        return True
    except:
        return False

def is_yaml_file(file_path)-> bool:
    try:
        with open(file_path,'r') as f:
            yaml.safe_load(f)
            return True
    except yaml.YAMLError:
        return False


def query_using_db(quer: str):
    client = chromadb.HttpClient(host="localhost",port="8000")
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template("""
    Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question""")
    vectordb = Chroma(embedding_function=config.embedding_model,client=client)
    qa = ConversationalRetrievalChain.from_llm(llm=config.llm_openai,
                                               retriever = vectordb.as_retriever(),
                                               condense_question_llm=CONDENSE_QUESTION_PROMPT,
                                               return_source_document=True,
                                               verbose=True
                                               )
    chat_history = []
    result = qa({"question": query,"chat_history": chat_history})
    print(result)

def load_and_embed_data(file_path: str,client,collection_name: str, file_type:str):

    if file_type == "pdf":
        #loader = PyPdfLoader(file_path,extract_images=False)
        #pages = loader.load_and_split()
        #print(f" Number of pages in pdf{file_path}: {len(pages)}")
        pages = []
        page_bucket= []
        for page in pages:
            page_bucket.append(page)
            if len(page_bucket) == config.EMBEDDING_MODEL_PAGE_REQUEST_LIMIT:
                Chroma.from_documents(documents=page_bucket,embedding=config.embedding_model,client=client,collection_name=collection_name)
                page_bucket.clear()
        #Left last chunk
        Chroma.from_documents(documents=page_bucket,embedding=config.embedding_model,client=client,collection_name=collection_name)

    elif file_type == "yaml":
        with open(file_path,'r') as f:
            raw_api_spec = yaml.load(f,loader=yaml.Loader)
            reduced_spec = reduce_openapi_spec(raw_api_spec,dereference=False)
            spec_str_list = [f"{reduced_spec.servers} {reduced_spec.description} {endpoint}" for endpoint in reduced_spec.endpoints]
        Chroma.from_texts(texts=spec_str_list,embedding=config.embedding_model,client=client,collection_name=collection_name)
        print(f"Added documents in collection:{collection_name}")

def print_collection(collection_name: str):
     client = chromadb.HttpClient(host="localhost",port="8000")    
     print(client.list_collections()) 
     collection = client.get_collection(collection_name)
     print(f"collection details: {collection}")
     print(f"document count:{collection.count()}")
     print(f"First document:{collection.peak(0)}")
    
def delete_collection(collection_name):
    client = chromadb.HttpClient(host="localhost",port="8000") 
    client.delete_collection(collection_name)
    print(f"collection {collection_name} deleted")


