from . import os, st, re, requests, stylable_container
from .BasePage import BasePage

from .modals import get_base64_image, create_call_modal, upload_call_modal_and_actions

class RouterAgent:
    def __call__(self, **kwargs):
        agent_prompt_slash_code = re.findall(r"(\/[\w\-_]*)? *(.*)", kwargs.get('prompt'))
        uri = agent_prompt_slash_code[0][0] or "/explain"
        prompt = agent_prompt_slash_code[0][1]
        print(f'{uri = }', f'{prompt = }')
        response = requests.post(os.getenv("BACKEND_URL", "http://127.0.0.1:5000") + f'{uri}', json = {"prompt" : prompt})
        if response.status_code != 200:
            st.error(f"Error: {response.text}")
            return
        response_json = response.json()
        print(f'{response_json = }')
        return response_json["message"]

class ChatModelPage(BasePage):
    def __init__(self):
        super().__init__()
        self.model = None
        self.router_agent = RouterAgent()

    def render(self):
        st.title("Dashboard")
        self.sidebar_elements()
        self.upfront_page()
        self.init_messages()
        self.reset_messages_sidebar_button()
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

    def upfront_page(self):
        tabs_and_dialogs_cols = st.columns(2)
        with tabs_and_dialogs_cols[0]:
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
            if clicked_create_call_button:upload_call_modal_and_actions()
        with tabs_and_dialogs_cols[1]:
            tabs = st.tabs(["Tasks"])
            func_of_tabs = [ self.tasks ]
            for tab, func in zip(tabs, func_of_tabs):
                with tab:func()

    def sidebar_elements(self):
        actions = {"Project" : self.projects, "Team" : self.team }
        with st.sidebar:
            for label, action in actions.items():
                st.header(label)
                action()
                st.divider()

    def team(self):
        teams_per_project = {"Projects": "Team1", "Projects2": "Team2", "Projects3": "Team3"}
        st.write(teams_per_project[st.session_state.selected_project])
        # st.image("static/2.png")

    def tasks(self):
        st.image("static/3.png")

    def projects(self):
        projects_available = ["Projects", "Projects2", "Projects3"]
        st.session_state.selected_project = st.selectbox("Projects available", projects_available)

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