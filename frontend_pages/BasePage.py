from . import st, ABC, abstractmethod

class BasePage(ABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BasePage, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.api_keys = []
            self.initialized = True

    @abstractmethod
    def render(self, keys : dict[str, str | None], **kwargs):
        if kwargs.get('on_sidebar', False):
            with st.sidebar:
                st.title("API Key Input")
                for key, default_value in keys.items():
                    st.session_state[key] = st.text_input(f"Enter API key for {key}", value=default_value, type="password")
                st.divider()
        else:
            st.title("API Key Input")
            for key, default_value in keys.items():
                st.session_state[key] = st.text_input(f"Enter API key for {key}", value=default_value, type="password")
            st.divider()
