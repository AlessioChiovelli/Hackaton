from . import os, st, re, requests
from .BasePage import BasePage

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
        st.title("Echo Bot")
        super().render({"WATSON_API_KEY": os.getenv("WATSON_API_KEY")})
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