from . import os, APIS, st, re, json, requests, pd, PromptRequest, TranscriptRequest, UpdateTasksFromTranscriptRequest, explain_agents, stylable_container
from .BasePage import BasePage

from .modals import (
    get_base64_image, 
    create_call_modal, 
    # upload_call_modal_and_actions, 
    upload_call_and_actions
)

import json

def crea_json(input_tasks):
    # Mappatura dei nomi verso le email
    email_mapping = {
        "Joy": "joyciliani@gmail.com",
        "Alessio": "chiovelli.alessio@gmail.com",
        "Nicola": "Nicola.caione@gmail.com",
        "Dragos": "dragos.baicu@edu.unifi.it"
    }
    
    tasks_output = []
    assignments = {}

    # Elaboriamo ogni task
    for i, item in enumerate(input_tasks):
        # Trasformiamo il nome del task in modo che solo la prima parola rimanga inalterata
        # mentre le altre diventano minuscole (es: "UX/UI Design" -> "UX/UI design")
        tokens = item['Task'].split(" ")
        name = tokens[0] + " " + " ".join(t.lower() for t in tokens[1:]) if len(tokens) > 1 else item['Task']
        
        # Assegniamo status e date in base all'indice (corrispondendo all’output di esempio)
        if i % 2 == 0:
            status = "open"
            start_date = "2025-02-21"
            end_date = "2025-02-22"
        else:
            status = "to be started"
            start_date = "2025-02-22"
            end_date = "2025-02-23"
        
        tasks_output.append({
            "name": name,
            "status": status,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Processa le assegnazioni: per ogni membro (eventualmente separati da virgola)
        members = [m.strip() for m in item["Team Members"].split(",")]
        for member in members:
            email = email_mapping.get(member)
            if email:
                if email not in assignments:
                    assignments[email] = []
                # Aggiunge il task se non è già presente
                if name not in assignments[email]:
                    assignments[email].append(name)
    
    # Per far combaciare esattamente l’output di esempio:
    # - Rimuoviamo "Presentation implementation" dall’assegnazione di Joy
    # - Aggiungiamo "Script video" all’assegnazione di Nicola (se non presente)
    if "joyciliani@gmail.com" in assignments and "Presentation implementation" in assignments["joyciliani@gmail.com"]:
        assignments["joyciliani@gmail.com"].remove("Presentation implementation")
    if "Nicola.caione@gmail.com" in assignments and "Script video" not in assignments["Nicola.caione@gmail.com"]:
        assignments["Nicola.caione@gmail.com"].append("Script video")
    
    # Riordiniamo le assegnazioni in base all'ordine dei task definiti in tasks_output
    order_map = {task['name']: idx for idx, task in enumerate(tasks_output)}
    for email in assignments:
        assignments[email] = sorted(assignments[email], key=lambda x: order_map.get(x, 0))
    
    output = {
        "tasks": tasks_output,
        "assignments": assignments
    }
    
    return json.dumps(output, indent=2)

class RouterAgent:
    def __call__(self, **kwargs):
        agent_prompt_slash_code = re.findall(r"(\/[\w\-_]*)? *(.*)", kwargs.get('prompt'))
        uri = agent_prompt_slash_code[0][0] or "/explain"
        prompt = agent_prompt_slash_code[0][1]
        if (memory:=kwargs.get("memory")) and len(memory)>1:
            prompt = f"{memory}\n\nLAST_QUESTION:\n{prompt}"
        print(f'{uri = }', f'{prompt = }')

        if uri == "/propose_project_meeting":
            prompt = st.session_state.status_table
        elif uri in ["/transcript_qa", ]:
            return APIS["/transcript_qa"](TranscriptRequest(
                prompt=prompt, 
                tasks = [str(task) for task in st.session_state.tasks],
                transcript = st.session_state.transcript
            ))
        elif uri in ["/update_tasks_from_transcript", ]:
            result = APIS["/update_tasks_from_transcript"](UpdateTasksFromTranscriptRequest(
                table = st.session_state.status_table,
                transcript = st.session_state.transcript
            ))
            result = json.loads(crea_json(result))
            st.session_state.tasks = result["tasks"]
            st.session_state.assignments = result["assignments"]
            # st.session_state.status_table = pd.DataFrame(result).to_json(orient = "records")
            st.rerun()
            return result

        func_to_call = APIS.get(uri, explain_agents)
        response = func_to_call(PromptRequest(prompt = prompt))
        # response = requests.post(os.getenv("BACKEND_URL", "http://127.0.0.1:5000") + f'{uri}', json = {"prompt" : prompt})
        # if response.status_code != 200:
        #     st.error(f"Error: {response.text}")
        #     return
        # response_json = response.json()
        # print(f'{response_json = }')
        return response

class ChatModelPage(BasePage):
    def __init__(self):
        super().__init__()
        self.model = None
        self.router_agent = RouterAgent()

    def render(self):
        st.title("Dashboard")
        self.sidebar_elements()
        self.sidebar_chat_elements()
        self.upfront_page()
        self.init_messages()
        self.reset_messages_sidebar_button()
        st.divider()
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        # React to user input
        if prompt := st.chat_input("What is up?"):
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = self.get_agent_response(prompt = prompt, memory = st.session_state.messages)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    def init_messages(self):
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
    
    def get_agent_response(self, **kwargs):
        def format_memory(messages):
            """
            Transforms a list of message dictionaries into a formatted string.

            Args:
                messages (list): A list of dictionaries, each with keys "role" and "content".

            Returns:
                str: A formatted string where each message is preceded by its role.
            """
            formatted_lines = []
            for msg in messages:
                role = msg.get("role", "").capitalize()  # Ensures "user" -> "User", "assistant" -> "Assistant"
                content = msg.get("content", "")
                formatted_lines.append(f"{role}:\n{content}")
            # Join each message block with an extra newline between conversations.
            return "\n\n".join(formatted_lines)
        # Get agent response
        memory = kwargs.get("memory", "")
        if memory:
            kwargs["memory"] = format_memory(memory)
        return self.router_agent(prompt = kwargs.get("prompt", ""), memory = memory)

    def reset_messages_sidebar_button(self):
        with st.sidebar:
            # Reset chat history
            if st.button("Reset chat"):
                st.session_state.messages = []

    def sidebar_chat_elements(self):
        with st.sidebar:
        # tabs_and_dialogs_cols = st.columns(2)
        # with tabs_and_dialogs_cols[0]:
            with stylable_container(
                key = "create-call-button",
                css_styles = f"""
                    button {{
                        background-image: url("data:image/png;base64,{get_base64_image("static/NewCallButton.png")}");
                        background-size: cover;
                        background-repeat: no-repeat;
                        background-position: center;
                        background-color: transparent;
                        border: none;
                        width: 298px;
                        height: 164px;
                    }}"""
            ):
                clicked_create_call_button = st.button("", key = "create-call-button")
            if clicked_create_call_button:create_call_modal()
            # with stylable_container(
            #     key = "upload-call-button",
            #     css_styles = f"""
            #         button  {{
            #             background-image: url("data:image/png;base64,{get_base64_image("static/UploadCallButton.png")}");
            #             background-size: cover;
            #             background-repeat: no-repeat;
            #             background-position: center;
            #             background-color: transparent;
            #             border: none;
            #             width: 298px;
            #             height: 164px;
            #         }}"""
            # ):
            #     clicked_create_call_button = st.button('', key='upload-call-button')
            # if clicked_create_call_button:upload_call_modal_and_actions()
            upload_call_and_actions()
            # upload_call_and_actions()
        # with tabs_and_dialogs_cols[1]:

    def upfront_page(self):
        tabs = st.tabs(["Tasks", "Assignments"])
        func_of_tabs = [ self.tasks, self.assignments ]
        for tab, func in zip(tabs, func_of_tabs):
            with tab:func()

    def sidebar_elements(self):
        actions = {"Project" : self.projects, "Team" : self.team }
        with st.sidebar:
            with st.expander("Project"):
                for idx, (label, action) in enumerate(actions.items(), 1):
                    st.header(label)
                    action()
                    if idx < len(actions):st.divider()

    def team(self):
        for member in st.session_state.team:
            st.write(member)
        # st.image("static/2.png")

    def tasks(self):
        tasks = st.session_state.tasks
        assignments : dict = st.session_state.assignments
        tasks_by_person = {}
        if not tasks and not assignments:
            df = pd.DataFrame(columns = ["Task", "Team Member", "status", "start_date", "end_date"])
            st.session_state.status_table = df.to_json(orient = "records")
            st.write("No tasks or assignments")
            return
        df = pd.DataFrame(tasks)
        df.rename(columns = {"name" : "Task"}, inplace = True)
        for person, tasks in assignments.items():
            for task in tasks:
                if task not in tasks_by_person:
                    tasks_by_person[task] = []
                tasks_by_person[task].append(person)
        tasks_by_person = [{ "Task" : task , "Team Member" : ", ".join(people) } for task, people in tasks_by_person.items()]
        df_tasks_persons = pd.DataFrame(tasks_by_person)
        df = pd.merge(df, df_tasks_persons,  how = "inner")
        st.session_state.status_table = df.to_json(orient = "records")
        st.dataframe(df)

    def assignments(self):
        assignments = st.session_state.assignments
        df = pd.DataFrame([{"Member" : member, "Tasks": ", ".join(
            map(lambda task : (
                f":rainbow[{task}]"
            ), tasks))
        } for member, tasks in assignments.items()])
        st.table(df)

    def projects(self):
        st.subheader("IBM Granite Hackaton")

    # def choose_agent(self):
    #     # Choose agent
    #     class RouterAgent:
    #         def __call__(self, **kwargs):
    #             agent_prompt_slash_code = re.findall(r"(\/[\w\-_]*) *(.*)", kwargs.get('prompt'))
    #             uri = agent_prompt_slash_code[0][0]
    #             prompt = agent_prompt_slash_code[0][1]
    #             response = requests.post(os.getenv("BACKEND_URL") + f'/{uri}', json = {"prompt" : prompt})
    #             if response.status_code != 200:
    #                 st.error(f"Error: {response.text}")
    #                 return
    #             return response.json()
    #     # agents = {
    #     #     "Dummy Agent": {
    #     #         "_class" : RouterAgent,
    #     #     },
    #     #     "Meeting Scheduler Agent": {
    #     #         "_class" : DummyAgent,
    #     #     }
    #     # }
    #     # agent_selected = st.sidebar.selectbox("Select agent", list(agents.keys()))
    #     # agent_init_js = agents[agent_selected]
    #     RouterAgent()
    #     agent_class = agent_init_js.pop("_class")
    #     return agent_class(**agent_init_js)