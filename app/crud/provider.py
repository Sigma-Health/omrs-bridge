"""
Provider-specific CRUD operations.
Extends BaseCRUD with provider-specific functionality including person and name joins.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base import BaseCRUD
from app.models import Provider, Person, PersonName
from app.schemas.provider import (
    ProviderResponse,
    ProviderListResponse,
    PersonInfo,
    PersonNameInfo,
)


class ProvidersCRUD(BaseCRUD[Provider]):
    """
    CRUD operations for Provider model.

    Provides provider-specific database operations including:
    - Basic CRUD operations (inherited from BaseCRUD)
    - Provider queries with person and name information
    """

    def __init__(self):
        super().__init__(Provider)

    def _build_full_name(self, person_name: PersonName) -> str:
        """
        Build full name from person_name components.

        Args:
            person_name: PersonName object

        Returns:
            Full name string
        """
        name_parts = []
        if person_name.prefix:
            name_parts.append(person_name.prefix)
        if person_name.given_name:
            name_parts.append(person_name.given_name)
        if person_name.middle_name:
            name_parts.append(person_name.middle_name)
        if person_name.family_name_prefix:
            name_parts.append(person_name.family_name_prefix)
        if person_name.family_name:
            name_parts.append(person_name.family_name)
        if person_name.family_name2:
            name_parts.append(person_name.family_name2)
        if person_name.family_name_suffix:
            name_parts.append(person_name.family_name_suffix)
        if person_name.degree:
            name_parts.append(person_name.degree)

        return " ".join(name_parts) if name_parts else None

    def _enrich_provider(self, provider: Provider, db: Session) -> ProviderResponse:
        """
        Enrich provider with person and person_name information.

        Args:
            provider: Provider object
            db: Database session

        Returns:
            ProviderResponse with person and name information
        """
        person_info = None
        person_name_info = None

        # Get person information if person_id exists
        if provider.person_id:
            person = (
                db.query(Person)
                .filter(
                    and_(
                        Person.person_id == provider.person_id,
                        Person.voided == False,  # noqa: E712
                    )
                )
                .first()
            )

            if person:
                person_info = PersonInfo(
                    person_id=person.person_id,
                    uuid=person.uuid,
                    gender=person.gender,
                    birthdate=person.birthdate,
                    birthdate_estimated=person.birthdate_estimated,
                    dead=person.dead,
                    death_date=person.death_date,
                    voided=person.voided,
                )

                # Get preferred person name
                person_name = (
                    db.query(PersonName)
                    .filter(
                        and_(
                            PersonName.person_id == provider.person_id,
                            PersonName.preferred == True,  # noqa: E712
                            PersonName.voided == False,  # noqa: E712
                        )
                    )
                    .first()
                )

                if person_name:
                    full_name = self._build_full_name(person_name)
                    person_name_info = PersonNameInfo(
                        person_name_id=person_name.person_name_id,
                        preferred=person_name.preferred,
                        prefix=person_name.prefix,
                        given_name=person_name.given_name,
                        middle_name=person_name.middle_name,
                        family_name_prefix=person_name.family_name_prefix,
                        family_name=person_name.family_name,
                        family_name2=person_name.family_name2,
                        family_name_suffix=person_name.family_name_suffix,
                        degree=person_name.degree,
                        full_name=full_name,
                    )

        # Build provider response
        return ProviderResponse(
            provider_id=provider.provider_id,
            person_id=provider.person_id,
            name=provider.name,
            identifier=provider.identifier,
            creator=provider.creator,
            date_created=provider.date_created,
            changed_by=provider.changed_by,
            date_changed=provider.date_changed,
            retired=provider.retired,
            retired_by=provider.retired_by,
            date_retired=provider.date_retired,
            retire_reason=provider.retire_reason,
            uuid=provider.uuid,
            role_id=provider.role_id,
            speciality_id=provider.speciality_id,
            provider_role_id=provider.provider_role_id,
            person=person_info,
            person_name=person_name_info,
        )

    def get_with_details(
        self, db: Session, provider_id: int
    ) -> Optional[ProviderResponse]:
        """
        Get provider by ID with person and name information.

        Args:
            db: Database session
            provider_id: Provider ID

        Returns:
            ProviderResponse with person and name information if found, None otherwise
        """
        provider = self.get(db, provider_id)
        if not provider:
            return None

        return self._enrich_provider(provider, db)

    def get_by_uuid_with_details(
        self, db: Session, uuid: str
    ) -> Optional[ProviderResponse]:
        """
        Get provider by UUID with person and name information.

        Args:
            db: Database session
            uuid: Provider UUID

        Returns:
            ProviderResponse with person and name information if found, None otherwise
        """
        provider = self.get_by_uuid(db, uuid)
        if not provider:
            return None

        return self._enrich_provider(provider, db)

    def list_with_details(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> ProviderListResponse:
        """
        List providers with person and name information.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            ProviderListResponse with enriched provider information
        """
        # Get total count
        total_count = db.query(self.model).count()

        # Get providers
        providers = self.list(db, skip=skip, limit=limit)

        # Enrich each provider
        enriched_providers = [
            self._enrich_provider(provider, db) for provider in providers
        ]

        return ProviderListResponse(
            providers=enriched_providers,
            total_count=total_count,
            skip=skip,
            limit=limit,
        )

