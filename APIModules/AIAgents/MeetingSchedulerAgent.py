from . import (
    os 
    , WatsonxLLM
    , PromptTemplate 
    , StrOutputParser
    , json
    # , JsonOutputParser
)

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
    "subject": "Update Meeting",
    "agenda": "Discuss upcoming deadlines",
    "start_date": "2025-02-21T10:00:00",
    "end_date": "2025-02-21T11:00:00",
    "participants": ["mario.rossi@example.com", "lucia.bianchi@example.com"]
}}

Return only the JSON, without any additional formatting.

Prompt:
{prompt}

"""

class MeetingSchedulerAgent:
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
    agent = MeetingSchedulerAgent(WATSON_API_KEY="YOUR_API_KEY_HERE")
    user_input = (
        "Organizza un meeting di aggiornamento con il team per discutere le prossime scadenze. "
        "Inizia il 2025-02-22 alle 22:00 e finisce alle 23:00. "
        "Invita chiovelli.alessio@gmail.com e nicola.caione@gmail.com ."
    )
    meeting_parameters = agent(user_input)
    print("Parametri per ScheduleMeeting:", meeting_parameters)
