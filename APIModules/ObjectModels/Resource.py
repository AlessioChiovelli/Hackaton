from . import *
from .Calendar import Calendar

class Resource(BaseModel):
    """
    Modello che rappresenta una risorsa (persona) con competenze e un calendario associato.
    """
    first_name: str = Field(..., description="Nome della persona")
    last_name: str = Field(..., description="Cognome della persona")
    skills: Optional[List[str]] = Field(None, description="Lista di competenze/skill della risorsa")
    monthly_cost: Optional[float] = Field(None, description="Costo mensile della risorsa")
    calendar: Optional[Calendar] = Field(None, description="Calendario associato a questa risorsa")