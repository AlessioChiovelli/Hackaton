import os
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv('.env')

# Scopes richiesti per accedere a Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]
OAUTH2_KEY = os.getenv("GOOGLE_OAUTH2_JSON_PATH", "desktop-client_secret_690889704678-5lml5g9dfva4hk1eugmhkbpn5atpnb8c.apps.googleusercontent.com.json")

# Autentica l'utente con OAuth 2.0 e restituisce il servizio Google Calendar API.
def authenticate_google():

    creds = None
    token_file = "token.json"

    # Se il token di accesso esiste, lo usa
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Se le credenziali non sono valide, richiede autenticazione
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                OAUTH2_KEY, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Salva il token per utilizzi futuri
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def ScheduleMeeting(subject: str, agenda: str, start_date: str, end_date: str, participants: list) -> str:
    """
    Crea un evento su Google Calendar con un link Google Meet.

    :param subject: Titolo del meeting
    :param agenda: Descrizione del meeting
    :param start_date: Data e ora di inizio (ISO format: '2025-02-21T10:00:00')
    :param end_date: Data e ora di fine (ISO format: '2025-02-21T11:00:00')
    :param participants: Lista di email degli invitati
    :return: ID dell'evento creato
    """
    try:
        service = authenticate_google()

        event = {
            "summary": subject,
            "description": agenda,
            "start": {"dateTime": start_date, "timeZone": "Europe/Rome"},
            "end": {"dateTime": end_date, "timeZone": "Europe/Rome"},
            "attendees": [{"email": email} for email in participants],
            "conferenceData": {
                "createRequest": {
                    "requestId": "meeting-" + start_date.replace(":", "-"),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            },
        }

        event = service.events().insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1
        ).execute()

        print(f"✅ Meeting created with ID: {event.get('id')}")
        return event.get("id")

    except Exception as e:
        print(f"❌ Error creating event: {e}")
        return None

# Restituisce gli intervalli occupati per un elenco di calendari tra start_time e end_time.
def get_free_busy(service, calendar_ids, start_time, end_time): # start_time e end_time sono oggetti datetime
    body = {
        "timeMin": start_time.isoformat() + "Z",
        "timeMax": end_time.isoformat() + "Z",
        "items": [{"id": calendar_id} for calendar_id in calendar_ids]
    }
    
    try:
        free_busy = service.freebusy().query(body=body).execute()
        busy_times = []

        for calendar_id in calendar_ids:
            if "busy" in free_busy["calendars"][calendar_id]:
                busy_times.extend(free_busy["calendars"][calendar_id]["busy"])

        # Converti i periodi occupati in datetime oggetti
        busy_intervals = [
            (datetime.fromisoformat(entry["start"][:-1]), datetime.fromisoformat(entry["end"][:-1]))
            for entry in busy_times
        ]

        return sorted(busy_intervals)
    
    except Exception as e:
        print(f"❌ Error fetching free/busy information: {e}")
        return []

# Trova il primo slot disponibile per tutti i partecipanti
def find_first_available_slot(service, calendar_ids, duration_minutes=30):

    now = datetime.now(timezone.utc)
    end_search = now + timedelta(days=7)  # Cerca nei prossimi 7 giorni

    step = timedelta(minutes=15)  # Incremento per il controllo
    meeting_duration = timedelta(minutes=duration_minutes)

    current_time = now.replace(second=0, microsecond=0) + timedelta(minutes=15)  # Evita slot troppo vicini
    while current_time < end_search:
        next_time = current_time + meeting_duration

        busy_intervals = get_free_busy(service, calendar_ids, current_time, next_time)

        # Se non ci sono sovrapposizioni, lo slot è libero
        if not any(start < next_time and end > current_time for start, end in busy_intervals):
            return current_time.isoformat()  # Primo slot disponibile

        # Prova il prossimo slot
        current_time += step

    return None  # Nessuno slot trovato



# Esempio di utilizzo:
if __name__ == "__main__":
    '''
    #Test - find an available slot among team members
    service = authenticate_google()
    calendar_ids = [""]
    slot = find_first_available_slot(service, calendar_ids)

    if slot:
        print(f"First available slot: {slot}")
    else:
        print("No slot found in the next 7 days")

    '''
    # #Test - schdule a meeting
    # meeting_id = ScheduleMeeting(
    #     subject="Project Kickoff Meeting",
    #     agenda="Discuss project progress and upcoming tasks.",
    #     start_date="2025-02-22T16:30:00",
    #     end_date="2025-02-22T17:30:00",
    #     participants=[""]
    # )
    # print("Meeting ID:", meeting_id)
    find_first_available_slot(authenticate_google())
   # '''