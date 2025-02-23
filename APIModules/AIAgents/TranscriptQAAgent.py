import os
from . import (
    WatsonxLLM, 
    PromptTemplate, 
    StrOutputParser, 
    AlertAgent, 
    Graph, 
    TypedDict, 
    START, END, 
    add_messages
)


TRANSCRIPT_QA_AGENT_PROMPT_TEMPLATE = """
You are an AI assistant for a project manager. 
Your task is to analize transcripts from Teams or Google meetings and answer questions about them. 
Additionally, you may receive tasks relevant to the context, and you should update the project manager on the progress of the project accordingly.

Please provide clear and concise answers to the following questions based on the meeting transcript.

***
TRANSCRIPT: {transcript}

***
QUESTION: {prompt}

***
TASKS: {tasks}
"""

TRANSCRIPT_UPDATE_TASKS_PROMPT_TEMPLATE = """
For each task listed in the json containing the table, 
update the cells in the “Task”, “Team Members”, “status”, “start_date” and “end_date” columns 
according to the information reported in the meeting transcript passed. 
Generate a json array with the keys “Task”, “Team Members”, “status”, “start_date” and “end_date” in this order.
Do not output any explanation, just return the json.

To be more clear, i want you to return an object that i can call with the function json.loads of python

Table:
{table}

TRANSCRIPT:
{transcript}
"""

class TranscriptQAAgent:
    def __init__(self, **kwargs):
        # Costruiamo la chain per la generazione della query SQL.
        self.transcript_qa_agent = (
            PromptTemplate.from_template(template=TRANSCRIPT_QA_AGENT_PROMPT_TEMPLATE)
            | WatsonxLLM(
                apikey=kwargs.get("WATSON_API_KEY", os.getenv("WATSON_API_KEY", None)),
                project_id=kwargs.get("WATSONX_PROJECT_ID", os.getenv("WATSONX_PROJECT_ID", None)),
                model_id=kwargs.get("model_id", os.getenv("WATSONX_MODEL_NAME", "ibm/granite-3-8b-instruct")),
                url="https://us-south.ml.cloud.ibm.com",
                params = {
                    "decoding_method": "sample",
                    "max_new_tokens": 3000,
                    "min_new_tokens": 1,
                    "temperature": 0.5,
                    "top_k": 50,
                    "top_p": 1,
                },
            )
            | StrOutputParser()
        )

    def __call__(self, prompt : str, transcript : str = None, tasks : str = None):
        
        return self.transcript_qa_agent.invoke({ "prompt" : prompt,  "transcript" : transcript or "",  "tasks" : tasks or ""})

class UpdateTaskFromTranscriptQAAgent:
    def __init__(self, **kwargs):
        # Costruiamo la chain per la generazione della query SQL.
        self.transcript_qa_agent = (
            PromptTemplate.from_template(template=TRANSCRIPT_UPDATE_TASKS_PROMPT_TEMPLATE)
            | WatsonxLLM(
                apikey=kwargs.get("WATSON_API_KEY", os.getenv("WATSON_API_KEY", None)),
                project_id=kwargs.get("WATSONX_PROJECT_ID", os.getenv("WATSONX_PROJECT_ID", None)),
                model_id=kwargs.get("model_id", os.getenv("WATSONX_MODEL_NAME", "ibm/granite-3-8b-instruct")),
                url="https://us-south.ml.cloud.ibm.com",
                params = {
                    "decoding_method": "sample",
                    "max_new_tokens": 5000,
                    "min_new_tokens": 1,
                    "temperature": 0.1,
                    "top_k": 50,
                    "top_p": 1,
                },
            )
            | StrOutputParser()
        )

    def __call__(self, table : str, transcript : str = None):
        
        return self.transcript_qa_agent.invoke({ "table" : table,  "transcript" : transcript})