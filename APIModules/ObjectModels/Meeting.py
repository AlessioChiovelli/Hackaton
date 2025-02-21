from . import *

class Meeting(BaseModel):
    """
    Modello che rappresenta una riunione o evento.
    """
    label: str = Field(..., description="Etichetta o titolo dell'evento")
    date: datetime = Field(..., description="Data e ora di inizio dell'evento")
    duration: timedelta = Field(..., description="Durata dell'evento")
    notes: Optional[str] = Field(None, description="Appunti/Agenda della riunione")
    transcript: Optional[str] = Field(None, description="Testo trascritto della riunione (per QA)")

    @property
    def end_datetime(self) -> datetime:
        """Calcola l'orario di fine basandosi sulla durata."""
        return self.date + self.duration
