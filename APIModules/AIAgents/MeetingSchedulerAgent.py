from datetime import datetime

from . import (
    os 
    , WatsonxLLM
    , PromptTemplate 
    , StrOutputParser
    , json
    # , JsonOutputParser
)

# Definizione del prompt template per l'agent
PROPOSE_MEETING_SCHEDULER_AGENT_PROMPT_TEMPLATE = f"""
Consider as input the following json containing informations about a table. 
Generate as output a single meeting invitation with exclusively these items:
    "subject": the title of the meeting (if it is not present in the input file, ask to the user)
    "agenda": a list called “Meeting agenda” only with the tasks that are in “open” or “to be started” status.  Do not consider tasks that are in “closed” state.
    "start_date": start date and time in ISO format (e.g., '2025-02-21T10:00:00'). If not present, make it in half an hour (consider that now is {datetime.now()}).
    "end_date": end date and time in ISO format (e.g., '2025-02-21T11:00:00'). If not present, make it as the start date + half an hour.
    "participants": a list called “Invited team members” with all the team members that have at least one task in “open” or “to be started” status
""" + """
Format the output using bullet points and escapes

Table:
{prompt}

"""
# Definizione del prompt template per l'agent
MEETING_SCHEDULER_AGENT_PROMPT_TEMPLATE = """
You are an assistant for meeting scheduling. Given a textual input describing a meeting, extract and generate a JSON object with the following fields:

"subject": the title of the meeting
"agenda": the description and/or topic of the meeting
"start_date": start date and time in ISO format (e.g., '2025-02-21T10:00:00')
"end_date": end date and time in ISO format (e.g., '2025-02-21T11:00:00')
"participants": a list of email addresses of the invitees
Ensure that all data is valid and correctly formatted.

For example, if the input is:
"Schedule an update meeting with the team to discuss upcoming deadlines. It starts on 2025-02-21 at 10:00 and ends at 11:00. Invite mario.rossi@example.com and lucia.bianchi@example.com."

The output should be:
{{
    "subject": "Project Update Meeting",
    "agenda": "Discuss upcoming deadlines",
    "start_date": "2025-02-21T10:00:00",
    "end_date": "2025-02-21T11:00:00",
    "participants": ["mario.rossi@example.com", "lucia.bianchi@example.com"]
}}

Return only the JSON, without any additional formatting.
""" + f"""
All the meetings should be scheduled for today or the following days.
Today is the""" + str(datetime.today()) + """

Prompt:
{prompt}

"""

class ProposerMeetingSchedulerAgent:
    def __init__(self, **kwargs):
        self.meeting_agent_chain = (
            PromptTemplate.from_template(template=PROPOSE_MEETING_SCHEDULER_AGENT_PROMPT_TEMPLATE)
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
    
    def __call__(self, prompt: str) -> str:
        return self.meeting_agent_chain.invoke({"prompt" : prompt})
        # return json.loads(self.meeting_agent_chain.invoke({"prompt" : prompt}))

class MeetingSchedulerAgentFromTable:
    def __init__(self, **kwargs):
        self.meeting_agent_chain = (
            PromptTemplate.from_template(template=MEETING_SCHEDULER_AGENT_PROMPT_TEMPLATE)
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
    
    def __call__(self, prompt: str) -> str:
        return json.loads(self.meeting_agent_chain.invoke({"prompt" : prompt}))

# Esempio d'uso:
if __name__ == "__main__":
    agent = MeetingSchedulerAgentFromTable(WATSON_API_KEY="YOUR_API_KEY_HERE")
    user_input = (
        "Organizza un meeting di aggiornamento con il team per discutere le prossime scadenze. "
        "Inizia il 2025-02-22 alle 22:00 e finisce alle 23:00. "
        "Invita chiovelli.alessio@gmail.com e nicola.caione@gmail.com ."
    )
    meeting_parameters = agent(user_input)
    print("Parametri per ScheduleMeeting:", meeting_parameters)
