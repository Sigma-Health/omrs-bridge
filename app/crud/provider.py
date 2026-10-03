"""
Provider-specific CRUD operations.
Extends BaseCRUD with provider-specific functionality including person and name joins.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, text

from .base import BaseCRUD
from app.models import Provider, Person, PersonName
from app.schemas.provider import (
    ProviderResponse,
    ProviderListResponse,
    ClinicalProviderLink,
    ClinicalProviderSearchResponse,
    PersonInfo,
    PersonNameInfo,
)
from app.sql.provider_sql import (
    CLINICAL_PROVIDER_FROM,
    PROVIDER_LIST_FROM,
    PROVIDER_LIST_SELECT,
)


def escape_like_pattern(term: str) -> str:
    """Escape SQL LIKE wildcards in user input."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def build_like_pattern(term: str) -> str:
    """Build case-insensitive substring LIKE pattern."""
    escaped = escape_like_pattern(term.strip())
    return f"%{escaped}%"


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

                # Get person name - prefer preferred, non-voided, but fall back to any non-voided
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

                # If no preferred name found, get any non-voided name (most recent first)
                if not person_name:
                    person_name = (
                        db.query(PersonName)
                        .filter(
                            and_(
                                PersonName.person_id == provider.person_id,
                                PersonName.voided == False,  # noqa: E712
                            )
                        )
                        .order_by(PersonName.person_name_id.desc())
                        .first()
                    )

                # If still no name found, get any name (even if voided) as last resort (most recent first)
                if not person_name:
                    person_name = (
                        db.query(PersonName)
                        .filter(PersonName.person_id == provider.person_id)
                        .order_by(PersonName.person_name_id.desc())
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
            person=person_info,
            person_name=person_name_info,
        )

    def _build_full_name_from_row(self, row) -> Optional[str]:
        name_parts = []
        for attr in (
            "name_prefix",
            "given_name",
            "middle_name",
            "family_name_prefix",
            "family_name",
            "family_name2",
            "family_name_suffix",
            "name_degree",
        ):
            val = getattr(row, attr, None)
            if val:
                name_parts.append(val)
        return " ".join(name_parts) if name_parts else None

    def _provider_response_from_row(self, row) -> ProviderResponse:
        person_info = None
        if getattr(row, "join_person_id", None):
            person_info = PersonInfo(
                person_id=row.join_person_id,
                uuid=row.person_uuid,
                gender=row.person_gender,
                birthdate=row.person_birthdate,
                birthdate_estimated=row.person_birthdate_estimated,
                dead=row.person_dead,
                death_date=row.person_death_date,
                voided=row.person_voided,
            )

        person_name_info = None
        if getattr(row, "person_name_id", None):
            full_name = self._build_full_name_from_row(row)
            person_name_info = PersonNameInfo(
                person_name_id=row.person_name_id,
                preferred=bool(row.name_preferred) if row.name_preferred is not None else False,
                prefix=row.name_prefix,
                given_name=row.given_name,
                middle_name=row.middle_name,
                family_name_prefix=row.family_name_prefix,
                family_name=row.family_name,
                family_name2=row.family_name2,
                family_name_suffix=row.family_name_suffix,
                degree=row.name_degree,
                full_name=full_name,
            )

        return ProviderResponse(
            provider_id=row.provider_id,
            person_id=row.person_id,
            name=row.name,
            identifier=row.identifier,
            creator=row.creator,
            date_created=row.date_created,
            changed_by=row.changed_by,
            date_changed=row.date_changed,
            retired=bool(row.retired) if row.retired is not None else None,
            retired_by=row.retired_by,
            date_retired=row.date_retired,
            retire_reason=row.retire_reason,
            uuid=row.uuid,
            person=person_info,
            person_name=person_name_info,
        )

    def get_with_details(
        self, db: Session, provider_id: int
    ) -> Optional[ProviderResponse]:
        """
        Get provider by ID with person and name information.
        """
        sql = f"""
{PROVIDER_LIST_SELECT}
{PROVIDER_LIST_FROM}
WHERE p.provider_id = :provider_id
LIMIT 1
"""
        row = db.execute(text(sql), {"provider_id": provider_id}).fetchone()
        if not row:
            return None
        return self._provider_response_from_row(row)

    def get_by_uuid_with_details(
        self, db: Session, uuid: str
    ) -> Optional[ProviderResponse]:
        """
        Get provider by UUID with person and name information.
        """
        sql = f"""
{PROVIDER_LIST_SELECT}
{PROVIDER_LIST_FROM}
WHERE p.uuid = :uuid
LIMIT 1
"""
        row = db.execute(text(sql), {"uuid": uuid}).fetchone()
        if not row:
            return None
        return self._provider_response_from_row(row)

    def list_with_details(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> ProviderListResponse:
        """
        List providers with person and name information (OpenMRS SQL).
        """
        count_row = db.execute(
            text("SELECT COUNT(*) AS cnt FROM provider p"),
        ).fetchone()
        total_count = int(count_row.cnt) if count_row else 0

        sql = f"""
{PROVIDER_LIST_SELECT}
{PROVIDER_LIST_FROM}
ORDER BY p.provider_id
LIMIT :limit OFFSET :skip
"""
        rows = db.execute(text(sql), {"limit": limit, "skip": skip}).fetchall()
        enriched_providers = [self._provider_response_from_row(row) for row in rows]

        return ProviderListResponse(
            providers=enriched_providers,
            total_count=total_count,
            skip=skip,
            limit=limit,
        )

    def _row_to_clinical_link(self, row) -> ClinicalProviderLink:
        given = row.given_name
        family = row.family_name
        parts = [p for p in (given, family) if p]
        display = " ".join(parts) if parts else None
        return ClinicalProviderLink(
            user_id=row.user_id,
            provider_id=row.provider_id,
            given_name=given,
            family_name=family,
            display_name=display,
        )

    def search_clinical_providers(
        self,
        db: Session,
        name: str,
        skip: int = 0,
        limit: int = 20,
    ) -> ClinicalProviderSearchResponse:
        """
        Search OpenMRS users with provider linkage by partial given/family name.
        """
        term = (name or "").strip()
        if len(term) < 2:
            return ClinicalProviderSearchResponse(
                results=[],
                total_count=0,
                skip=skip,
                limit=limit,
            )

        pattern = build_like_pattern(term)
        name_filter = """
          AND (
            LOWER(COALESCE(pn.given_name, '')) LIKE LOWER(:pattern)
            OR LOWER(COALESCE(pn.family_name, '')) LIKE LOWER(:pattern)
            OR LOWER(CONCAT_WS(' ', pn.given_name, pn.family_name))
              LIKE LOWER(:pattern)
          )
        """
        base_where = f"""
WHERE p.provider_id IS NOT NULL
  AND COALESCE(p.retired, 0) = 0
  AND COALESCE(u.retired, 0) = 0
{name_filter}
"""
        count_sql = f"SELECT COUNT(*) AS cnt {CLINICAL_PROVIDER_FROM} {base_where}"
        count_row = db.execute(text(count_sql), {"pattern": pattern}).fetchone()
        total_count = int(count_row.cnt) if count_row else 0

        select_sql = f"""
SELECT u.user_id, p.provider_id, pn.given_name, pn.family_name
{CLINICAL_PROVIDER_FROM}
{base_where}
ORDER BY pn.family_name, pn.given_name, u.user_id
LIMIT :limit OFFSET :skip
"""
        rows = db.execute(
            text(select_sql),
            {"pattern": pattern, "limit": limit, "skip": skip},
        ).fetchall()
        results = [self._row_to_clinical_link(row) for row in rows]
        return ClinicalProviderSearchResponse(
            results=results,
            total_count=total_count,
            skip=skip,
            limit=limit,
        )

    def lookup_clinical_provider(
        self,
        db: Session,
        user_id: int,
        provider_id: int,
    ) -> Optional[ClinicalProviderLink]:
        """
        Resolve display name for an OpenMRS user_id + provider_id pair.
        """
        select_sql = f"""
SELECT u.user_id, p.provider_id, pn.given_name, pn.family_name
{CLINICAL_PROVIDER_FROM}
WHERE u.user_id = :user_id
  AND p.provider_id = :provider_id
LIMIT 1
"""
        row = db.execute(
            text(select_sql),
            {"user_id": user_id, "provider_id": provider_id},
        ).fetchone()
        if not row:
            return None
        return self._row_to_clinical_link(row)
