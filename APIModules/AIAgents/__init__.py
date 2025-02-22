import os
import json
from dotenv import load_dotenv
from langchain_ibm import WatsonxLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langgraph.graph import StateGraph as Graph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


_ = load_dotenv('.env')
