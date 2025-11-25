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
from .drugs import DrugsCRUD
from .order_types import OrderTypesCRUD
from .visits import VisitsCRUD
from .vitals import VitalsCRUD
from .provider import ProvidersCRUD

# Initialize CRUD instances for easy access
concepts = ConceptsCRUD()
diagnoses = DiagnosesCRUD()
encounters = EncountersCRUD()
observations = ObservationsCRUD()
orders = OrdersCRUD()
drugs = DrugsCRUD()
order_types = OrderTypesCRUD()
visits = VisitsCRUD()
vitals = VitalsCRUD()
providers = ProvidersCRUD()

__all__ = [
    "BaseCRUD",
    "ConceptsCRUD",
    "DiagnosesCRUD",
    "EncountersCRUD",
    "ObservationsCRUD",
    "OrdersCRUD",
    "DrugsCRUD",
    "OrderTypesCRUD",
    "VisitsCRUD",
    "VitalsCRUD",
    "ProvidersCRUD",
    "concepts",
    "diagnoses",
    "encounters",
    "observations",
    "orders",
    "drugs",
    "order_types",
    "visits",
    "vitals",
    "providers",
]
