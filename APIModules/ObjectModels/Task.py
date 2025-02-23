from . import *

class Task(BaseModel):
    """
    Modello che rappresenta un task di progetto.
    """
    name: str = Field(..., description="Nome del task")
    status: Optional[str] = Field(None, description="Stato del task")  # Aggiunto
    start_date: Optional[date] = Field(None, description="Data di inizio del task")
    end_date: Optional[date] = Field(None, description="Data di fine prevista del task")
