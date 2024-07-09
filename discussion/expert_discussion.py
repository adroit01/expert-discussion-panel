import copy
import time
from langchain.schema import HumanMessage
from experts import prompts
from experts.expert import DetailerExpert,SummarizerExpert,Status
import config.llm_config as config
from langchain.prompts.prompt import PromptTemplate
import uuid
#import config.speech_config as speech_config

class ExpertDiscussion:

    def __init__(self):
        self.experts_list = []
        self.discussion_prompt_template = PromptTemplate(input_variables=["word_count", "topic", "others_statements"],
                                                         template=prompts.DISCUSSION_PROMPT)
        self.TOTAL_DISCUSSION_ROUND = 1
        self.summarizer = SummarizerExpert(uuid.uuid4().hex, "Summary Creator","Summarizer","""
                                          You are very good at summzarization of the duscussion and able to capture 
                                          very clear understanding of subject matter once you go through the discssion text,
                                          you manke out the summary with great articualtion and details""",
                                          "Google's Gemini Pro", config.llm_gemini_pro)
        
        self.stop: bool = False

    def __deepcopy__(self,memo):
        new_instance = type(self)()
        new_instance.experts_list = copy.deepcopy(x=self.experts_list,memo=memo)
        new_instance.discussion_prompt_template = copy.deepcopy(x=self.discussion_prompt_template,memo=memo)
        new_instance.stop = copy.deepcopy(x=self.stop,memo=memo)
        return new_instance
    
    def set_disussion_round(self,disucssion_rounds: int):
        self.TOTAL_DISCUSSION_ROUND = disucssion_rounds
        print("Disucssion round changed")
        return
    
    def delete_expert(self,expert_id: str):
        for i in range(len(self.experts_list)):
            if self.experts_list[i].id == expert_id:
                found_expert = self.experts_list[i]
                self.experts_list.remove(found_expert)
                return found_expert
        return None
    
    def add_expert(self,name,role, specialization, llm_type, verbosity,lookup, collection_name):
        new_expert = DetailerExpert(uuid.uuid4().hex,name,role,specialization,llm_type,config.llm_types.get(llm_type),
                                    verbosity_level=verbosity,lookup=lookup,collection_name=collection_name)
        self.experts_list.append(new_expert)
        print(f"Expert with id:{new_expert.id} added")
        return new_expert
    
    def get_expert_list(self):
        return self.experts_list
    
    def set_stop(self,stop: bool):
        self.stop = stop

    def get_stop(self):
        return self.stop
    
    def start_discussion(self,topic: str):
        print("*****Discussion Starts Here*****")
        responses_of_all_experts = []
        self.stop = False
        for expert in self.experts_list:
            expert.warmup()
            expert.set_status(Status.Idle)
        print(f"Count of Experts in panel:{len(self.experts_list)}")
        discussion_statements = {}
        round=1

        while round <= self.TOTAL_DISCUSSION_ROUND:
            if self.stop:
                break
            for expert in self.experts_list:
                if self.stop:
                    break
                print(f"Discussion Round: {round} Expert:{expert.name}-{expert.id}")

                prompt = self.discussion_prompt_template.format(others_statements=responses_of_all_experts,
                                                                topic=topic,
                                                                word_count=expert.verbosity_level)
                response = expert.think_and_respond(HumanMessage(content=prompt),self.experts_list,self.stop)

                responses_of_all_experts.append(response)
            round += 1
            #Delay between rounds of discussion
            time.sleep(1)
        
        for expert in self.experts_list:
            expert.set_status(Status.Idle)
            discussion_statements[f"Name:{expert.name} Id:{expert.id}"] = expert.responses
        print(discussion_statements)
        print("*****Discussion Ends Here*****")
        return discussion_statements

    def summarization(self,topic):
        print("*****Summarization Starts Here*****")
        discussion_responses = self.start_discussion(topic)
        #discussion_summary = "Not Summarized"
        if(discussion_responses and len(discussion_responses) > 0):
            discussion_summary = self.summarizer.summarize(topic,discussion_responses)
        print("*****Summarization Ends Here*****")
        return discussion_summary
    
    #def speech_to_text(self)-> str:
    #    return speech_config.speech_to_text()

