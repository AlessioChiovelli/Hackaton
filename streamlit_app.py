from frontend_pages import st
from frontend_pages.ConfigPage import ConfigPage
from frontend_pages.ChatModelPage import ChatModelPage
from frontend_pages.Dashboard import Dashboard

st.set_page_config(layout="wide")

PAGES = {
    "Configurazione": ConfigPage,
    "Dashboard": ChatModelPage,
    # "Dashboard": Dashboard,
}

if __name__ == "__main__":
    PAGES[st.sidebar.selectbox("Select a page", list(PAGES.keys()))]().render()
    # PAGES["Chat with AI Model"]().render()