import json
import os.path
import chromadb
from langchain.schema.messages import HumanMessage,SystemMessage
from langchain.vectorstores.chroma import Chroma
from experts import prompts
import langchain
from langchain.prompts import PromptTemplate,SystemMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder,HumanMessagePromptTemplate
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import StructuredOutputParser,ResponseSchema
from enum import StrEnum
import time
from utils import common_utils
import config.llm_config as config
import requests
#import config.speech_config as speech

langchain.debug = True

class Status(StrEnum):
    Idle = "Idle"
    Speaking = "Speaking"
    Thinking = "Thinking"
    Listening = "Listening"

class Expert:
    def __init__(self, id: str, name: str, role: str, specialization: str,
                  llm_type: str, llm, verbosity_level: int = 50, lookup: bool= False, collection_name: str= None):
        self.id = id
        self.name = name
        self.role = role
        self.status = Status.Idle
        self.speaking_lag = 0.05
        self.verbosity_level = verbosity_level
        self.specialization= specialization
        self.llm_type = llm_type
        self.average_response_delay = None
        self.llm = llm
        self.lookup = lookup
        self.human_response = None
        self.human_respponse_arrived = False
        self.responses = []
        self.systemMessage = SystemMessagePromptTemplate.from_template(prompts.EXPERT_SYSTEM_PROMPT).format(role=self.role,specialization=self.specialization)
        self.prompt = ChatPromptTemplate.from_messages([
            #The persistent system prompt
            SystemMessage(content=self.systemMessage.content),
            #where the memory will be stored.
            MessagesPlaceholder(variable_name = "statement_history"),
            #Where input will be injected
            HumanMessagePromptTemplate.from_template("{human_message}") 
        ])
        self.collection_name = collection_name
        self.conversation_buffer_memory = ConversationBufferMemory(memory_key="statement_history",return_messages=True)
        
        if self.llm_type != "human" :
            if self.llm_type == "Google's Gemini Pro":
                self.conversation_llm_chain = self.llm
            else:

                if not self.lookup:
                    self.conversation_llm_chain = LLMChain(llm = self.llm, prompt = self.prompt, verbose=True, memory=self.conversation_buffer_memory)
                
                else:
                    client = chromadb.HttpClient(host='localhost',port="8000")
                    vectordb = Chroma(embedding_function=config.embedding_model, client = client, collection_name=self.collection_name)
                    self.conversation_llm_chain = ConversationalRetrievalChain.from_llm(llm=self.llm,
                                                                                        retriever=vectordb.as_retriever(),
                                                                                        condense_question_llm=self.prompt,
                                                                                        return_source_documents=True,
                                                                                        verbose=True)

    def warmup(self):
        self.responses = []
        if self.llm_type != "human":
            self.conversation_buffer_memory.clear()
        self.average_response_delay = None

    def about_expert(self):
        print(f"id:{self.id}, Name:{self.name},Role:{self.role}, Specialization: {self.spcialization}, powered by llm:{self.llm}")

    def set_speaker_speed(self,speed_factor: float):
        self.speaking_lag = self.speaking_lag / speed_factor
        print("Expert Speaking  lag changed to",self.speaking_lag)
        return

    def set_status(self, status:Status):
        self.status= status

    def slow_echo(self,response,stop):
        for i in range(len(response)):
            time.sleep(self.speaking_lag)
            if(stop):
                break
            yield response[:i + 1]
    
def workaround_gemini_call(query: str):
    print("Gemini:",query)
    payload = {"contents": [{"parts":[{"text":f"{query}"}]}]}
    response = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=AIzaSyAk4RyIN7fIi1f2loyDC6JAkZBCoKUr2kA"
                             ,headers={"Content-Type": "application/json"},
                             json=payload)
    json_response = json.loads(response.text)
    return json_response['candidates'][0]['content']['parts'][0]['text']

class DetailerExpert(Expert):

    def set_other_experts_status(self,expert_list,status:Status):

        for e in expert_list:
            if e.id == self.id:
                continue
            e.status = status
        return
    
    def get_human_response(self):

        while not self.human_respponse_arrived:
            print("Awaiting for human response")
            time.sleep(1)
        self.human_respponse_arrived - False
        return self.human_response

    def set_human_response(self,response: str):
        self.human_response = response
        self.human_respponse_arrived = True

    
    def lookup_information(self,source_directory: str):
        if not self.lookup:
            return
        
        if os.path.exists(source_directory):
            print(f"{source_directory} exists")
            files = chromadb.HttpClient(host='localhost', port ='8000')

            for file in files:
                print(file)
                file_path = os.path.jin(source_directory,file)
                if file_path.endswith(".pdf"):
                    common_utils.load_and_embed_data(file_path,self.client,self.collection_name,"pdf")
                elif file_path.endswith('.yaml'):
                    common_utils.load_and_embed_data(file_path,self.client,self.collection_name,"yaml")
                
        else:
            print(f"{source_directory} Path is invalid")

    
    def think_and_respond(self,humanMessage: HumanMessage, expert_list,stop) -> str:

        response = ""
        self.responses.append(response)
        index = len(self.responses)

        try:
            self.status = Status.Thinking
            start_time = time.time()
            response = ""

            #Human as Expert
            if(self.llm_type == 'human'):
                response =self.get_human_response()

            #Google's LLM
            elif(self.llm_type == "Google's Gemini Pro"):
                response = workaround_gemini_call(humanMessage.content)

            #Any other LLM
            else:
                #Refer Embeddings i.e. RAG
                if self.lookup:
                    response_dict = self.conversation_llm_chain({"human_message": humanMessage.content,"question": humanMessage.content,
                                                                 "chat_history": []})
                    response = response_dict["answer"]

                else:
                    response = self.conversation_llm_chain.predict(human_message=humanMessage.content)

            
            if self.average_response_delay == None:
                self.average_response_delay = round((time.time() - start_time),3)
            
            else:
                avg_elapsed_time = (self.average_response_delay + (time.time() - start_time))/2
                self.average_response_delay = round(avg_elapsed_time,3)

            self.status = Status.Speaking
            self.set_other_experts_status(expert_list,Status.Listening)
            #speech.speech_synthesizer.speak_text_async(response.replace("*",''))
            for sub_response in self.slow_echo(response,stop):
                self.responses[index - 1] = sub_response
            print("Responses of this Expert",self.responses)   
        except Exception as e:
            print(f"Exception occurred: {e}")
            response = "Error: Sorry but I am not able to respond."
            self.responses[index -1] = response
        
        finally:
            self.status = Status.Idle
            self.set_other_experts_status(expert_list,Status.Idle)
        return response
    

class SummarizerExpert(Expert):

    def __init__(self, id: str, name: str, role: str, specialization: str, llm_type: str, llm, verbosity_level: int = 50, lookup: bool = False, collection_name: str = None):
        super().__init__(id, name, role, specialization, llm_type, llm, verbosity_level, lookup, collection_name)
        self.systemMessage = PromptTemplate.from_template(prompts.SUMMARIZER_SYSTEM_PROMPT).format(role=self.role,specialization=self.specialization)

        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=self.systemMessage),
                HumanMessagePromptTemplate.from_template(prompts.SUMMARIZER_PROMPT)
            ]
            
        )

    def summarize(self,topic,discussion_statements: dict)->str:
        output_formatting_dict = self.format_instructions()
        llm_chain = LLMChain(llm=self.llm,prompt=self.prompt)
        summary = llm_chain.predict(topic=topic,discussion_statements=discussion_statements,
                                    format_instructions = output_formatting_dict["format_instructions"],convert_system_message_to_human=True)
        print(summary)
        response_dict = output_formatting_dict["parser"].parse(summary)
        self.responses.append(response_dict)
        return response_dict
    
    def format_instructions(self):
        topic_schema = ResponseSchema(name="topic",description="It is topic of discussion",type="str")
        summary_schema = ResponseSchema(name="summary",description="It is summary of discussion",type="str")
        action_item_present_schema = ResponseSchema(name="actionItemPresent",
                                                    description="True if any specific action item is present in summary of discussion",type="bool")
        action_item_schema = ResponseSchema(name="actionItem",description="sepcific action Items",type="object")

        ouput_parser = StructuredOutputParser(response_schemas=[topic_schema,summary_schema,action_item_present_schema,action_item_schema])

        format_instructions = ouput_parser.get_format_instructions()
        return {"parser": ouput_parser,"format_instructions": format_instructions}
    




        



            