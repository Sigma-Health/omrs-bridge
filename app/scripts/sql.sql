SELECT 
    c.concept_id,
    c.uuid,
    fs.name AS fully_specified_name,
    GROUP_CONCAT(DISTINCT syn.name ORDER BY syn.name SEPARATOR '; ') AS synonyms,
    GROUP_CONCAT(DISTINCT sh.name ORDER BY sh.name SEPARATOR '; ') AS short_names,
    GROUP_CONCAT(DISTINCT cd.description ORDER BY cd.description SEPARATOR '; ') AS descriptions,
    dt.name AS datatype
FROM concept_set cs
JOIN concept c ON cs.concept_id = c.concept_id

-- Fully specified name (English, preferred if available)
LEFT JOIN concept_name fs ON fs.concept_id = c.concept_id
    AND fs.concept_name_type = 'FULLY_SPECIFIED'
    AND fs.locale = 'en'

-- Synonyms (English)
LEFT JOIN concept_name syn ON syn.concept_id = c.concept_id
    AND syn.concept_name_type = 'SYNONYM'
    AND syn.locale = 'en'

-- Short names (English)
LEFT JOIN concept_name sh ON sh.concept_id = c.concept_id
    AND sh.concept_name_type = 'SHORT'
    AND sh.locale = 'en'

-- Descriptions (English)
LEFT JOIN concept_description cd ON cd.concept_id = c.concept_id
    AND cd.locale = 'en'

-- Datatype
LEFT JOIN concept_datatype dt ON dt.concept_datatype_id = c.datatype_id

WHERE cs.concept_set = 24431
GROUP BY c.concept_id, c.uuid, fs.name, dt.name;
