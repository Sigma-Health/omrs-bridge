"""
CRUD package for database operations.
Provides class-based CRUD operations with separation of concerns.
"""

from .base import BaseCRUD
from .concepts import ConceptsCRUD
from .encounters import EncountersCRUD
from .observations import ObservationsCRUD
from .orders import OrdersCRUD

# Initialize CRUD instances for easy access
concepts = ConceptsCRUD()
encounters = EncountersCRUD()
observations = ObservationsCRUD()
orders = OrdersCRUD()

__all__ = [
    "BaseCRUD",
    "ConceptsCRUD", 
    "EncountersCRUD",
    "ObservationsCRUD",
    "OrdersCRUD",
    "concepts",
    "encounters", 
    "observations",
    "orders"
]