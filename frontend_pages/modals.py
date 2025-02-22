from . import st, base64, os
from .load_css import render_css


def get_base64_image(image_path : str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
    
@st.dialog("Create a Call")
def create_call_modal():
    st.write("This is the content of your modal")
    st.multiselect("People", ["Alice", "Bob", "Charlie"])
    st.multiselect("Tasks", ["Task 1", "Task 2", "Task 3"])
    st.text_area("Prompt")
    buttons = [
        ("submit", lambda _ : st.balloons()), 
        ("cancel", lambda _ : st.balloons())
    ]
    cols = st.columns(len(buttons))
    for col, button in zip(cols, buttons): 
        with col:
            if st.button(button[0]):
                button[1]()

@st.dialog("Upload a Call")
def upload_call_modal_and_actions():
    st.write("This is the content of your modal")
    uploaded_file = st.file_uploader(
        "Import a videocall recording or its transcripts", 
        type=['.txt', '.doc', '.docx', '.pdf', '.mp4', '.wav', '.flac'],
        accept_multiple_files=False
    )
    buttons = {
        "Crea minuta": minuta_action_from_uploaded_call, 
        "Genera trascritto": transcript_action_from_uploaded_call, 
        "Genera Task": create_tasks_action_from_uploaded_call, 
    }
    func = buttons[st.selectbox("Choose an action", buttons.keys())]()
                
def minuta_action_from_uploaded_call():
    if st.button("Crea minuta"):
        st.download_button("Scarica minuta", data = "moc_minuta.txt")

def transcript_action_from_uploaded_call():
    if st.button("Crea transcript"):
        st.download_button("Scarica transcript", data = "moc_transcript.txt")

def create_tasks_action_from_uploaded_call():
    import random
    if st.button("create_tasks"):
        st.session_state.tasks = [f'task_{i}' for i in range(random.randint(1, 10))]
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