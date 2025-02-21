from . import *
from .Task import Task

class Project(BaseModel):
    """
    Modello che rappresenta un progetto, con budget, date e lista di task associati.
    """
    name: str = Field(..., description="Nome del progetto")
    budget: Optional[float] = Field(None, description="Budget del progetto")
    start_date: Optional[date] = Field(None, description="Data di inizio del progetto")
    end_date: Optional[date] = Field(None, description="Data di fine effettiva del progetto")
    tasks: List[Task] = Field(default_factory=list, description="Lista di task associati al progetto")
