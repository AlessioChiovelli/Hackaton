from . import os, st
from .BasePage import BasePage

class ChatModelPage(BasePage):
    def __init__(self):
        super().__init__()
        self.model = None

    def render(self):
        super().render({"WATSON_API_KEY": os.getenv("WATSON_API_KEY")})
        agent = self.choose_agent()
        self.init_messages()
        self.reset_messages_sidebar_button()
        st.title("Echo Bot")
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
            response = self.get_agent_response(agent = agent, prompt = prompt)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    def init_messages(self):
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
    
    def choose_agent(self):
        # Choose agent
        class DummyAgent:
            def __call__(self, **kwargs):return "I'm a dummy agent"

        agents = {
            "Dummy Agent": {
                "_class" : DummyAgent,
            },
            "Meeting Scheduler Agent": {
                "_class" : DummyAgent,
            }
        }
        agent_selected = st.sidebar.selectbox("Select agent", list(agents.keys()))
        agent_init_js = agents[agent_selected]
        agent_class = agent_init_js.pop("_class")
        return agent_class(**agent_init_js)
    
    def get_agent_response(self, agent, **kwargs):
        # Get agent response
        return agent(**kwargs)

    def reset_messages_sidebar_button(self):
        with st.sidebar:
            # Reset chat history
            if st.button("Reset chat"):
                st.session_state.messages = []