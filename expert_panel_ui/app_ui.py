import gradio as gr
from discussion.expert_discussion import ExpertDiscussion

experts = []

def update_expert_dataframe(exp_holder):
    total_exp_count = len(exp_holder)
    if total_exp_count == 0:
        return [None,None]
    expert_group_details = []
    expert_group_details_for_tag = []
    for i in range(total_exp_count):
        expert_details  = [exp_holder[i].id,exp_holder[i].name,exp_holder[i].role,exp_holder[i].specialization,
                      exp_holder[i].llm_type,exp_holder[i].verbosity_level]
        expert_details_for_tag = [f"{exp_holder[i].name} a {exp_holder[i].role} powered by {exp_holder[i].llm_type}",exp_holder[i].status,"",""]
        expert_group_details.append(expert_details)
        expert_group_details_for_tag.append(expert_details_for_tag)
    return [expert_group_details,expert_group_details_for_tag]

def add_expert(name,role,specialization, llm_type,lookup,create_knowledge_base_check_box,
               doc_directory,verbosity,exp_holder,exp_discussion_panel:ExpertDiscussion,collection_name):
    new_expert = exp_discussion_panel.add_expert(name,role,specialization,llm_type,verbosity,lookup,collection_name)
    if lookup and create_knowledge_base_check_box:
        new_expert.lookup_information(doc_directory)
    exp_holder.append(new_expert)
    print(f"New Expert added in panel having Id:{new_expert.id} Name:{new_expert.name}")
    return update_expert_dataframe(exp_holder)

def remove_expert_by_id(expert_id,exp_holder,exp_discussion_panel:ExpertDiscussion):
    if len(expert_id) == 0:
        raise gr.Error("Expert Id missing")
    deleted_expert = exp_discussion_panel.delete_expert(expert_id)
    if deleted_expert == None:
        raise gr.Error(f"Expert with Id:{expert_id} not found")
    
    for i, expert in enumerate(exp_holder):
        if expert.id == deleted_expert.id:
            exp_holder.remove(expert)
        print(f"Expert with Id:{deleted_expert.id} deleted")
        break
    return update_expert_dataframe(exp_holder)



def refresh_experts(exp_holder,exp_discussion_panel:ExpertDiscussion):
    exp_list = exp_discussion_panel.get_expert_list()
    exp_holder = [exp_list[i] for i in range(len(exp_list))]
    return update_expert_dataframe(exp_holder)

def init_discussion_tab(exp_holder):
    expert_group_details_for_tag = []
    total_exp_count = len(exp_holder)
    for i in range(total_exp_count):
        expert_details_for_tag = [f"{exp_holder[i].name} a {exp_holder[i].role} powered by {exp_holder[i].llm_type}",exp_holder[i].status,None,""] 
        expert_group_details_for_tag.append(expert_details_for_tag)
    
    return [expert_group_details_for_tag, ""]

def update_response(exp_holder):

    if exp_holder == None or len(exp_holder) == 0:
        return None
    dataframe = []
    total_exp_count = len(exp_holder)
    for i in range(total_exp_count):
        exp_details = f"{exp_holder[i].name} a {exp_holder[i].role} powered by {exp_holder[i].llm_type}" 
        exp_status = exp_holder[i].status
        exp_avg_response_time = exp_holder[i].average_response_delay
        statements = []
        for j in range(len(exp_holder[i].responses)):
            statements.append(f"*** Round:{j+1} statement::{exp_holder[i].responses[j]}")
        exp_group = [exp_details,exp_status,exp_avg_response_time,statements]
        dataframe.append(exp_group)
    return dataframe

def set_discussion_round(round: int, exp_discussion_panel:ExpertDiscussion):
    exp_discussion_panel.set_disussion_round(round)
    return

def set_speaker_speed(exp_holder, speed_factor):
    for exp in exp_holder:
        exp.set_speaker_speed(speed_factor)
    return

def stop_discussion(exp_discussion_panel: ExpertDiscussion):
    exp_discussion_panel.set_stop(True)
    return 

def submit_human_response(exp_holder, response):
    for exp in exp_holder:
        if exp.llm_type == 'human':
            exp.set_human_response(response=response)
    return

def start_discussion(topic,exp_discssion_panel: ExpertDiscussion):
    response = exp_discssion_panel.summarization(topic=topic)
    return response

callback = gr.CSVLogger()

def speech_to_text_ui(exp_discssion_panel:ExpertDiscussion):
    text = exp_discssion_panel.speech_to_text()
    return text

with gr.Blocks(title="Expert Discussion Panel",css = "footer {display:none !important}") as demo:
    gr.Markdown("""
               # Expert Discussion Panel!
                Powered by network of Opena and Proprietory LLMs """)
    exp_holder = gr.State([])
    ePanel = gr.State(ExpertDiscussion())
    with gr.TabItem("Expert Enrollment") as exp_enroll:
        with gr.Group() as exp_grp:
            with gr.Row() as exp:
                name_inp = gr.Textbox(lines=1,label="Name",placeholder="Name")
                role_inp = gr.Textbox(lines=1,label="Role",placeholder="Role")
                poweredByLLM = gr.Dropdown(
                    choices=["OpenAI-GPT-3.5 Turbo",
                              "Google's Gemini Pro",
                              "Meta-llama3-8B-Instruct",
                              "human"],
                    label="Powered by LLM")
                verbose_slider = gr.Slider(1,1001,value=100,step=5,interactive=True,label="Verbosity")
            with gr.Row():
                specialization_inp = gr.Textbox(lines=3,label="Specialization",placeholder="Specialization",scale=1)
            with gr.Row():
                lookup_check_box = gr.Checkbox(label="lookup",value=False,visible=True)
                knowledgeBase_drp_down = gr.Dropdown(choices = ["Sample-Collection"],
                                                     allow_custom_value=True,
                                                     label="Knowledge Base")
                create_knowledge_base_check_box = gr.Checkbox(label="Create KnowledgeBase",value=False, visible=True)
                doc_directory = gr.Textbox(lines=1,placeholder="documents directory path", label="Knowledge base",
                                           scale=3,visible=True)
            with gr.Row():
                btn_add_expert = gr.Button("Add", scale=1)
            with gr.Group() as exp_details_section:
                expert_details_dataframe = gr.DataFrame(
                    None,
                    headers=["Id","Name","Role","Specialization","poweredBy","verbosity"],
                    wrap=True,
                    datatype=["markdown","markdown","markdown","markdown","markdown","markdown"],
                    interactive=False,
                    label="Enrolled Experts"
                )
                with gr.Row():
                    remove_expert_txtBox = gr.Textbox(lines=1,label="",placeholder="Enter Id")
                    remove_expert_btn = gr.Button("Remove")
                    refresh_expert_btn = gr.Button("Refresh Expert List")
            gr.Examples([
                [
                "Amit",
                "Software Development Expert",
                """ You have worked on various software development projects. you have a very good understanding of computer science command in java and python as programming language. A machine learning enthusiast and Generative Artificial Intelligence Expert""",
                "Google's Gemini Pro"
                ],
                [
                "Sumit",
                "Software Development Expert",
                """ You have worked on various software development projects. you have a very good understanding of computer science command in java and python as programming language. A machine learning enthusiast and Generative Artificial Intelligence Expert""",
                "Google's Gemini Pro"
                ],
                [
                "Niraj",
                "Travel Planner",
                """You have a huge experience of planning a travel. worked in various company as Travel planner and manager and guide. Visited almost every places in India.""",
                "Google's Gemini Pro"
                ],
                [
                "Sanjay",
                "Player1",
                """Amateur Player""",
                "Google's Gemini Pro"
                ],
                [
                "Raghav",
                "Player2",
                """Amateur Player""",
                "Google's Gemini Pro"
                ],
                 [
                "Raj",
                "Player3",
                """Amateur Player""",
                "Google's Gemini Pro"
                ]
            ],
            inputs=[name_inp,role_inp,specialization_inp,poweredByLLM,exp_holder,ePanel],
            fn=add_expert)

    #Expert Discussion Tab
    with gr.TabItem("Expert Discussion Panel") as discussion_panel:
        with gr.Row():
            discussion_topic_inp_txt = gr.Textbox(lines=3,label="Discussion Topic", scale=2)
            audio_capture = gr.Audio(sources="microphone",label="Set the Topic",container=False,format="mp3",show_label=True,visible=False)
            discussion_round_slider = gr.Slider(1,10,value=1,step=1,interactive=True,label="Discussion Rounds")
            speaker_speed_slider = gr.Slider(1,10,value=1,step=1,interactive=True,label="Speaker Speed")

        gr.Examples([
            "How to use Error and create a Robust self healing system",
            "Step by step process to masster python programming language",
            "Explaination of existence of Wormhole",
            "Concept of Blackhole",
            "Plan a 3 days trip to Goa for a family of 3 members(husband,wife and daughter)",
            "How to have a healthy relation between husband and wife",
            """Solve this puzzle: there are 90 camels and 9 Hooks, tie all 90 camels in 9 hooks such that each hook has only odd numnber of camels""",
            """Let us all play a game. You need to name a color. Do not repeat the color which is already been said by other player. if repeated you loose the game"""],
        inputs=[discussion_topic_inp_txt])
        with gr.Row():
            btn_start = gr.Button("Start",scale=1)
            btn_stop = gr.Button("Stop",scale=1) 
        expert_tag_dataframe = gr.DataFrame(
        headers=["Expert Details", "Status","Avg. Resp. Time(Sec)", "Statements"],
        wrap=True,
        datatype=["str","str","str","str"],
        interactive=True,
        label="Experts Suggestions",
        column_widths=["150px","85px","75px","800px"],
        )

        with gr.Row() as human_response:
            human_inpt_txt = gr.Textbox(lines=2,label="Human",placeholder="human Response", visible=True)
            human_response_btn  = gr.Button("Respond")
        with gr.Row() as summary:
            summary_output = gr.Textbox(lines=10,label="Expert Disucssion Summary")
        flag_btn = gr.Button("Save the Discussion")
        audio_capture.start_recording(fn=speech_to_text_ui,inputs=[ePanel],outputs=[discussion_topic_inp_txt])
        btn_start.click(fn=start_discussion,inputs=[discussion_topic_inp_txt,ePanel],outputs=summary_output)
        btn_start.click(fn=init_discussion_tab,inputs=exp_holder,outputs=[expert_tag_dataframe,summary_output])
        btn_start.click(fn=update_response,inputs=exp_holder,outputs=[expert_tag_dataframe],trigger_mode="multiple",every=0.1)
        btn_stop.click(fn=stop_discussion,inputs=ePanel,outputs=None)
        discussion_round_slider.change(fn=set_discussion_round,inputs=[discussion_round_slider,ePanel],outputs=None)
        speaker_speed_slider.change(fn=set_speaker_speed,inputs=[exp_holder,speaker_speed_slider],outputs=None)
        human_response_btn.click(fn=submit_human_response,inputs=[exp_holder,human_inpt_txt],outputs=None)
        callback.setup([discussion_topic_inp_txt,expert_tag_dataframe,summary_output],"flagged_data_points")
        flag_btn.click(lambda *args: callback.flag(args),[discussion_topic_inp_txt,expert_tag_dataframe,summary_output],None,
                       preprocess=False)
        
    with gr.TabItem("Knowledge Management") as knowledgebase_panel:
        gr.Markdown(""" The feature to create knowledgebase which can be referred by Expert is under development""")
    
    btn_add_expert.click(fn=add_expert,
                    inputs=[name_inp,role_inp,specialization_inp,poweredByLLM,lookup_check_box,create_knowledge_base_check_box,doc_directory,verbose_slider
                            ,exp_holder,ePanel,knowledgeBase_drp_down],
                    outputs=[expert_details_dataframe,expert_tag_dataframe])
    remove_expert_btn.click(fn=remove_expert_by_id,
                            inputs=[remove_expert_txtBox,exp_holder,ePanel],
                            outputs=[expert_details_dataframe,expert_tag_dataframe])
    refresh_expert_btn.click(fn=refresh_experts,
                                inputs=[exp_holder,ePanel],
                                outputs=[expert_details_dataframe,expert_tag_dataframe])

#demo.queue().launch(share=False,server_name="0.0.0.0",server_port=7860,auth=[("admin","password"),"anchor","enter123"],auth_message="Please enter login details")    
demo.queue().launch(share=False,server_name="0.0.0.0",server_port=7860)


                

    

