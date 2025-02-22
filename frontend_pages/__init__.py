import streamlit as st
import requests
import re
import os
import base64
from abc import ABC, abstractmethod
from functools import  partial
from streamlit_calendar import calendar
from streamlit_extras.stylable_container import stylable_container