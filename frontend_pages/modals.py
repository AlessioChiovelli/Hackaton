import random
import docx
from PyPDF2 import PdfFileReader
import io

from . import st, base64, os, requests, partial, PromptRequest, APIS
from .load_css import render_css

st.markdown(f'<style></style>', unsafe_allow_html=True)

def get_base64_image(image_path : str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
    
@st.dialog("Create a Call")
def create_call_modal():
    team_members_selected = st.multiselect("People", options = st.session_state.team)
    tasks_selected = st.multiselect("Tasks", options = filter(lambda task: task['status'] not in ["to be started", "finished"], st.session_state.tasks))
    prompt = st.text_area("Prompt", value = "\n\n".join(
        [
            "\n".join(["Team Members:", *map(lambda x : f'\t{x}', team_members_selected)]),
            "\n".join(["Tasks:", *[str(task) for task in tasks_selected]]),
        ]
    ))
    buttons = [
        ("submit", lambda prompt : APIS['/call'](PromptRequest(prompt = prompt))), 
    ]
    cols = st.columns(len(buttons))
    for col, button in zip(cols, buttons): 
        with col:
            if st.button(button[0]):
                button[1](prompt)

@st.dialog("Upload a Call")
def upload_call_modal_and_actions():
    uploaded_file = st.file_uploader(
        # "Import a videocall recording or its transcripts", 
        "Import a videocall recording transcript", 
        type=['.txt', '.doc', '.docx', '.pdf'],
        # type=['.txt', '.doc', '.docx', '.pdf', '.mp4', '.wav', '.flac'],
        accept_multiple_files=False
    )
    transcript_text = get_transcript_text(uploaded_file) if uploaded_file else ""
    buttons = {
        # "Crea minuta": minuta_action_from_uploaded_call, 
        # "Genera trascritto": transcript_action_from_uploaded_call, 
        "QA from transcripts": partial(qa_from_transcripts, Transcript = transcript_text), 
        "Generate Tasks from transcript": partial(create_tasks_action_from_uploaded_call_transcript, Transcript = transcript_text), 
    }
    _ = buttons[st.selectbox("Choose an action", buttons.keys())]()

def upload_call_and_actions():
    uploaded_file = st.file_uploader(
        # "Import a videocall recording or its transcripts", 
        "Import a videocall recording transcript", 
        type=['.txt', '.doc', '.docx', '.pdf'],
        # type=['.txt', '.doc', '.docx', '.pdf', '.mp4', '.wav', '.flac'],
        accept_multiple_files=False
    )
    transcript_text = get_transcript_text(uploaded_file) if uploaded_file else ""
    st.session_state.transcript = transcript_text
    if os.getenv("DEBUG_MODE", True):
        with st.expander("Transcript"):
            st.text_input("", value = transcript_text)
                
def minuta_action_from_uploaded_call():
    if st.button("Crea minuta"):
        st.download_button("Scarica minuta", data = "moc_minuta.txt")

def transcript_action_from_uploaded_call():
    if st.button("Crea transcript"):
        st.download_button("Scarica transcript", data = "moc_transcript.txt")
    
def get_transcript_text(uploaded_file):
    if uploaded_file is not None:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension == '.txt':
            return get_text_from_txt(uploaded_file)
        elif file_extension in ['.doc', '.docx']:
            return get_text_from_doc(uploaded_file)
        elif file_extension == '.pdf':
            return get_text_from_pdf(uploaded_file)
    return ""

def get_text_from_txt(uploaded_file):
    return uploaded_file.read().decode("utf-8")

def get_text_from_doc(uploaded_file):
    doc = docx.Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])

def get_text_from_pdf(uploaded_file):
    reader = PdfFileReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page_num in range(reader.getNumPages()):
        text += reader.getPage(page_num).extract_text()
    return text


def qa_from_transcripts(Transcript : str):
    Prompt = st.text_area("Prompt")
    Transcript = st.text_area("Transcript")
    Tasks = "\n\n".join(st.multiselect("Tasks", options = ["Task 1", "Task 2", "Task 3"]))
    if st.button("QA from transcripts"):
        response = requests.post(os.getenv("QA_TRANSCRIPT_ENDPOINT", "http://127.0.0.1:5000/transcript") , 
            json = {
                "prompt": Prompt,
                "transcript" : Transcript or "",
                "tasks": Tasks or [],
            })
        st.success(response.json())
        return 

def create_tasks_action_from_uploaded_call_transcript(Transcript : str):

    if st.button("create_tasks"):
        response = requests.post(os.getenv("QA_TRANSCRIPT_ENDPOINT", "http://127.0.0.1:5000/tasks/from_transcript") , json = {"transcript" : Transcript})
        st.session_state.tasks = st.success(response.json())
        return 
    if st.session_state.get('tasks'):
        task = st.selectbox("Select a task", st.session_state.tasks)
        task_matchmaking(task)

def task_matchmaking(task : str):
    cols = st.columns(2)
    with cols[0]:
        st.markdown("### Task matchmaking")
    with cols[1]:
        st.multiselect("People", ["Alice", "Bob", "Charlie"])
    if st.button("Assign"):
        st.success("Task assigned")