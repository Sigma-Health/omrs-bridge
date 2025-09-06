"""
CRUD package for database operations.
Provides class-based CRUD operations with separation of concerns.
"""

from .base import BaseCRUD
from .concepts import ConceptsCRUD
from .encounters import EncountersCRUD
from .observations import ObservationsCRUD
from .orders import OrdersCRUD
from .order_types import OrderTypesCRUD
from .visits import VisitsCRUD

# Initialize CRUD instances for easy access
concepts = ConceptsCRUD()
encounters = EncountersCRUD()
observations = ObservationsCRUD()
orders = OrdersCRUD()
order_types = OrderTypesCRUD()
visits = VisitsCRUD()

__all__ = [
    "BaseCRUD",
    "ConceptsCRUD",
    "EncountersCRUD",
    "ObservationsCRUD",
    "OrdersCRUD",
    "OrderTypesCRUD",
    "VisitsCRUD",
    "concepts",
    "encounters",
    "observations",
    "orders",
    "order_types",
    "visits",
]
