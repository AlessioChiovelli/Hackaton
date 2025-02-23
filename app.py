from frontend_pages import st
from frontend_pages.ConfigPage import ConfigPage
from frontend_pages.ChatModelPage import ChatModelPage


# PAGES = {
#     "Dashboard": ChatModelPage,
#     # "Configurazione": ConfigPage,
# }

if __name__ == "__main__":
    ChatModelPage().render()
    # PAGES["Chat with AI Model"]().render()