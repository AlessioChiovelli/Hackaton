from . import *

class Task(BaseModel):
    """
    Modello che rappresenta un task di progetto.
    """
    name: str = Field(..., description="Nome del task")
    start_date: Optional[date] = Field(None, description="Data di inizio del task")
    end_date: Optional[date] = Field(None, description="Data di fine prevista del task")
    project_name: Optional[str] = Field(None, description="Nome del progetto a cui è associato il task")
    sub_tasks: Optional[List[str]] = Field(None, description="Lista di sub-task o risorse collegate")
