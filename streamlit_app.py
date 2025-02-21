from frontend_pages import st
from frontend_pages.ChatModelPage import ChatModelPage

PAGES = {
    "Chat with AI Model": ChatModelPage
}

if __name__ == "__main__":
    PAGES[st.selectbox("Select a page", list(PAGES.keys()))]().render()