# Expert Discussion Panel
This is an Expert Discussion Panel powered by Large Language Models.

## Highlights of this Application
It is based on concept that if different Experts powered by different LLMs are made to sit in a discussion panel discussing among each other on a topic then they can bring out different and pioneer perspective and new opinion to solve the problem underlying the topic under debate.

## Following LLMs are integrated for use.
1. Meta's llama3-8B-Instruct
2. Google's Gemini Pro
3. OPENAI GPT-3.5-turbo

## Installation and Running the application
1. clone this git repository 
    git clone https://github.com/adroit01/expert-discussion-panel.git
2. cd expert-discssion-panel
3. create a dedicated python environment using conda or virtualenv
4. pip install -r requirements.txt
5. download and install ollama from https://ollama.com/download , easiest way to run llama model locally
    run in terminal: ollama run llama3
6. rename example.env to .env and set required Keys mentioned for integrating with various LLM.
7. export PYTHONPATH=path to the installed repo
8. Run python expert_panel_ui/app_ui.py

## Using Application
Open in browser http://localhost:7860
1. Enrollment of Expert : Use <b>Expert Enrollment Tab</b> to add one ore more experts as required in disucssion panel.
2. Expert Discussion Panel: Use this tab to start and stop discussion on any topic few are enlisted as example there.
