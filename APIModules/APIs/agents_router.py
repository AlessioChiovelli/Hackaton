from pydantic import BaseModel
from fastapi import APIRouter

base_router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

@base_router.post("/explain")
async def explain_agents(request : PromptRequest):
    actions = [
        {
            "command" : "/calendar", 
            "action" : "Create a calendar",
            "example-messages" : [
                "/calendar Create a new calendar with Joy and Nicola where we will talk about the dashboard",
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

@base_router.post("/creare_call")
async def create_call(request : PromptRequest):
    return {
        "message" : "stai creando una call",
    }

@base_router.post("/upload_call")
async def upload_call(request : PromptRequest):
    return {
        "message" : "hai caricato",
    }