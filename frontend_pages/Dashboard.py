from . import os, st, stylable_container
from .BasePage import BasePage

from .modals import get_base64_image, create_call_modal, upload_call_modal_and_actions

class Dashboard(BasePage):
    def render(self):
        st.title("Dashboard")
        super().render(keys={"WATSON_API_KEY": os.getenv("WATSON_API_KEY")})
        self.upfront_page()

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
            tabs = st.tabs(["Team", "Tasks", "Progetti"])
            func_of_tabs = [ self.team, self.tasks, self.projects]
            for tab, func in zip(tabs, func_of_tabs):
                with tab:func()

    def team(self):
        st.image("static/2.png")

    def tasks(self):
        st.image("static/3.png")

    def projects(self):
        st.write("Projects")