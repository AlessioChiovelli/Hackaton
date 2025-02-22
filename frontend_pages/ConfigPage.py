from . import os
from .BasePage import BasePage

class ConfigPage(BasePage):
    def render(self):
        super().render(keys={"WATSON_API_KEY": os.getenv("WATSON_API_KEY")})