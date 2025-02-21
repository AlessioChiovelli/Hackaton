from . import *
from .Meeting import Meeting

class Calendar(BaseModel):
    """
    Modello che rappresenta un calendario, contenente una lista di riunioni/eventi.
    """
    name: str = Field(..., description="Nome del calendario (es. 'Calendario Apple', 'Google Calendar')")
    meetings: List[Meeting] = Field(default_factory=list, description="Lista di riunioni/eventi presenti nel calendario")
