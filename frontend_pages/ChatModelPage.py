from . import os, APIS, st, re, json, requests, pd, PromptRequest, TranscriptRequest, explain_agents, stylable_container
from .BasePage import BasePage

from .modals import (
    get_base64_image, 
    create_call_modal, 
    # upload_call_modal_and_actions, 
    upload_call_and_actions
)

class RouterAgent:
    def __call__(self, **kwargs):
        agent_prompt_slash_code = re.findall(r"(\/[\w\-_]*)? *(.*)", kwargs.get('prompt'))
        uri = agent_prompt_slash_code[0][0] or "/explain"
        prompt = agent_prompt_slash_code[0][1]
        print(f'{uri = }', f'{prompt = }')
        func_to_call = APIS.get(uri, explain_agents)
        response = func_to_call(
            PromptRequest(prompt = prompt) 
            if uri != "" else 
            TranscriptRequest(
                prompt=prompt, 
                tasks = json.dumps(self.session_state.tasks),
                transcript = self.session_state.transcript
            )
        )
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
            response = self.get_agent_response(prompt = prompt)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    def init_messages(self):
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
    
    def get_agent_response(self, **kwargs):
        # Get agent response
        return self.router_agent(**kwargs)

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
            with stylable_container(
                key = "upload-call-button",
                css_styles = f"""
                    button  {{
                        background-image: url("data:image/png;base64,{get_base64_image("static/UploadCallButton.png")}");
                        background-size: cover;
                        background-repeat: no-repeat;
                        background-position: center;
                        background-color: transparent;
                        border: none;
                        width: 298px;
                        height: 164px;
                    }}"""
            ):
                clicked_create_call_button = st.button('', key='upload-call-button')
            # if clicked_create_call_button:upload_call_modal_and_actions()
            if clicked_create_call_button:upload_call_and_actions()
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
        df = pd.DataFrame(tasks)
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