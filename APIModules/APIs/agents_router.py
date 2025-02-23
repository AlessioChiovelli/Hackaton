import json
import re
from typing import Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from APIModules.AIAgents.MeetingSchedulerAgent import ProposerMeetingSchedulerAgent, MeetingSchedulerAgentFromTable as MeetingSchedulerAgent
from APIModules.AIAgents.TranscriptQAAgent import TranscriptQAAgent, UpdateTaskFromTranscriptQAAgent
from google_calendar import ScheduleMeeting

base_router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str


@base_router.post("/propose_project_meeting")
def propose_call(request : PromptRequest):
    return json.dumps(ProposerMeetingSchedulerAgent()(request.prompt))

@base_router.post("/send_call")
def create_call(request : PromptRequest):
    # return json.dumps(MeetingSchedulerAgent()(request.prompt))
    return ScheduleMeeting(**MeetingSchedulerAgent()(request.prompt))

class TranscriptRequest(BaseModel):
    prompt: str
    transcript: str = ""
    tasks: list[str] = []

@base_router.post("/transcript_qa")
def transcript_qa(request : TranscriptRequest):
    transcript_qa_agent = TranscriptQAAgent()
    return transcript_qa_agent(**{
        'prompt': request.prompt,
        'transcript': request.transcript,
        'tasks': "\n".join([''] + [f'{task}' for task in request.tasks])
        }
    )
# from APIModules.AIAgents.SQLAgent import SQLAgent

# class QueryResponse(BaseModel):
#     sql: str
#     results: List[Any] = []
#     message: str = "Query eseguita con successo."

# @base_router.post("/query")
# async def execute_query(request: PromptRequest):
#     try:
#         # Inizializza lo SQLAgent con le credenziali necessarie (sostituisci i valori appropriati)
#         sql_agent = SQLAgent()
#         # Lo SQLAgent trasforma il prompt in una query SQL, esegue la query e restituisce (query, risultati)
#         sql_query, results = sql_agent(request.prompt)
#         return QueryResponse(sql=sql_query, results=results)
#     except Exception as e:
#         # Se l'AlertAgent ha bloccato la query oppure si è verificato un altro errore,
#         # restituisci un messaggio d'errore
#         raise HTTPException(status_code=400, detail=str(e))

class UpdateTasksFromTranscriptRequest(BaseModel):
    table: str
    transcript: str

@base_router.post("/update_tasks_from_transcript")
def mod_tasks_from_transcript(request : UpdateTasksFromTranscriptRequest):

    output_json_str :str = UpdateTaskFromTranscriptQAAgent()(**request.model_dump())
    output_json_str = re.sub(r'\[json\]', '', output_json_str)
    return json.loads(output_json_str)


@base_router.post("/explain")
def explain_agents(request : PromptRequest):
    actions = [
        {"command" : "/explain", "action" : "explains the available commands", "example-messages" : ["explain"]}
        , {"command" : "/propose_project_meeting", "action" : "Proposes a new meeting by reading the task lists and the transcript in the session so that the user can later on modify the promt and  create a gmeet calendar", "example-messages" : ["/propose_project_meeting"]}
        , {"command" : "/send_call", "action" : "Creates a new gmeet calendar", "example-messages" : ["/call Create a new call with mail@example.com at 6 PM on 2025-02-22 for 2 hours"]}
        , {"command" : "/call", "action" : "Creates a new gmeet calendar", "example-messages" : ["/call Create a new call with mail@example.com at 6 PM on 2025-02-22 for 2 hours"]}
        , {"command" : "/transcript_qa", "action" : "makes a qa session on the given transcript of a video call", "example-messages" : []}
        , {"command" : "/tasks_from_transcript", "action" : "updates the transcripts of the page from a command", "example-messages" : ['/tasks_from_transcript']}
        , {"command" : "/update_tasks_from_transcript", "action" : "updates the transcripts of the page from a command", "example-messages" : ['/tasks_from_transcript']}
    ]
    return "\n".join(
                [
                    "You can interact with an agent by simply doing a /{command} {and asking something in the prompt}",
                    "Here's the available agents, commands, actions and some examples:"
                ] + 
                [
                    f"-  Command: {action['command']}\n"
                    f"-  Action: {action['action']}\n"
                    f"-  Example messages:\n" + "\n".join(
                        [f"    - {example}" for example in action["example-messages"]]
                    )
                    for action in actions
                ])

APIS = {
    "" : explain_agents, 
    "/explain" : explain_agents, 
    "/propose_project_meeting" : propose_call,
    "/send_call" : create_call,
    "/call" : create_call,
    "/transcript_qa" : transcript_qa, 
    "/tasks_from_transcript" : transcript_qa, 
    "/update_tasks_from_transcript" : mod_tasks_from_transcript, 
}