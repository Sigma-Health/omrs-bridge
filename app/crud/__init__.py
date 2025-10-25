"""
CRUD package for database operations.
Provides class-based CRUD operations with separation of concerns.
"""

from .base import BaseCRUD
from .concepts import ConceptsCRUD
from .diagnoses import DiagnosesCRUD
from .encounters import EncountersCRUD
from .observations import ObservationsCRUD
from .orders import OrdersCRUD
from .order_types import OrderTypesCRUD
from .visits import VisitsCRUD
from .vitals import VitalsCRUD

# Initialize CRUD instances for easy access
concepts = ConceptsCRUD()
diagnoses = DiagnosesCRUD()
encounters = EncountersCRUD()
observations = ObservationsCRUD()
orders = OrdersCRUD()
order_types = OrderTypesCRUD()
visits = VisitsCRUD()
vitals = VitalsCRUD()

__all__ = [
    "BaseCRUD",
    "ConceptsCRUD",
    "DiagnosesCRUD",
    "EncountersCRUD",
    "ObservationsCRUD",
    "OrdersCRUD",
    "OrderTypesCRUD",
    "VisitsCRUD",
    "VitalsCRUD",
    "concepts",
    "diagnoses",
    "encounters",
    "observations",
    "orders",
    "order_types",
    "visits",
    "vitals",
]
