import streamlit as st
import requests
import re
import json
import os
import base64
import pandas as pd
from abc import ABC, abstractmethod
from functools import  partial
from streamlit_calendar import calendar
from streamlit_extras.stylable_container import stylable_container
from APIModules.APIs.agents_router import (
    PromptRequest,
    TranscriptRequest,
    explain_agents,
    APIS
)