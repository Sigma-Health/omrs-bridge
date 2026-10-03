"""
OpenMRS provider SQL (users, provider, person, person_name).
"""

# Best non-voided person_name per person (preferred first, then newest).
def _best_person_name_predicate(person_id_sql: str) -> str:
    return f"""pn.person_name_id = (
    SELECT pn2.person_name_id
    FROM person_name pn2
    WHERE pn2.person_id = {person_id_sql}
      AND pn2.voided = 0
    ORDER BY pn2.preferred DESC, pn2.person_name_id DESC
    LIMIT 1
  )"""


CLINICAL_PROVIDER_FROM = f"""
FROM users u
LEFT JOIN provider p ON p.person_id = u.person_id
LEFT JOIN person_name pn ON pn.person_id = u.person_id
  AND pn.voided = 0
  AND {_best_person_name_predicate("u.person_id")}
"""

PROVIDER_LIST_FROM = f"""
FROM provider p
LEFT JOIN person per ON per.person_id = p.person_id
LEFT JOIN person_name pn ON pn.person_id = p.person_id
  AND pn.voided = 0
  AND {_best_person_name_predicate("p.person_id")}
"""

PROVIDER_LIST_SELECT = """
SELECT
  p.provider_id,
  p.person_id,
  p.name,
  p.identifier,
  p.creator,
  p.date_created,
  p.changed_by,
  p.date_changed,
  p.retired,
  p.retired_by,
  p.date_retired,
  p.retire_reason,
  p.uuid,
  per.person_id AS join_person_id,
  per.uuid AS person_uuid,
  per.gender AS person_gender,
  per.birthdate AS person_birthdate,
  per.birthdate_estimated AS person_birthdate_estimated,
  per.dead AS person_dead,
  per.death_date AS person_death_date,
  per.voided AS person_voided,
  pn.person_name_id,
  pn.preferred AS name_preferred,
  pn.prefix AS name_prefix,
  pn.given_name,
  pn.middle_name,
  pn.family_name_prefix,
  pn.family_name,
  pn.family_name2,
  pn.family_name_suffix,
  pn.degree AS name_degree
"""
