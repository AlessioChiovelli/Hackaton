from typing import Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from APIModules.AIAgents.MeetingSchedulerAgent import MeetingSchedulerAgent
# from APIModules.AIAgents.SQLAgent import SQLAgent
from APIModules.AIAgents.TranscriptQAAgent import TranscriptQAAgent
from google_calendar import ScheduleMeeting

base_router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str


@base_router.post("/call")
async def create_call(request : PromptRequest):
    return ScheduleMeeting(**MeetingSchedulerAgent()(request.prompt))

class TranscriptRequest(BaseModel):
    transcript: str = ""
    prompt: str
    tasks: list[str] = []

@base_router.post("/transcript")
async def upload_call(request : TranscriptRequest):
    transcript_qa_agent = TranscriptQAAgent()
    return transcript_qa_agent(**{
        'prompt': request.prompt,
        'transcript': request.transcript,
        'tasks': "\n".join([''] + [f'{task}' for task in request.tasks])
        }
    )

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

@base_router.post("/explain")
async def explain_agents(request : PromptRequest):
    actions = [
        {
            "command" : "/calendar", 
            "action" : "Create a new calendar object to Google Calendar. It needs the following fields: [subject, agenda, start_date, end_date, participants]",
            "example-messages" : [
                "/call schedule a meeting with joy@gmail.com for the Hackaton today at 7PM for 2 h",
            ],
        },
        {
            "command" : "/transcript", 
            "action" : "Does a Question and Answer session on a transcript. It needs the following fields: [transcript, prompt, tasks]. They can also be passed as a single message.",
            "example-messages" : [
                "/transcript what happened in the meeting with the team today? give me a summary, and filter the infos regarding task 1, 2 and 3. Here's the transcript: ...",
            ],
        },
    ]
    return {
            "message" : "\n".join(
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
                ]),
        }

