-- =========================================
-- FUNCTIONS
-- =========================================

-- 1. Search contacts by pattern
CREATE OR REPLACE FUNCTION search_contacts(pattern_text TEXT)
RETURNS TABLE (
    contact_id INT,
    first_name VARCHAR,
    last_name VARCHAR,
    phone_number VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.contact_id, p.first_name, p.last_name, p.phone_number
    FROM phonebook p
    WHERE p.first_name ILIKE '%' || pattern_text || '%'
       OR p.last_name ILIKE '%' || pattern_text || '%'
       OR p.phone_number ILIKE '%' || pattern_text || '%';
END;
$$ LANGUAGE plpgsql;


-- 2. Pagination function
CREATE OR REPLACE FUNCTION get_contacts_paginated(limit_count INT, offset_count INT)
RETURNS TABLE (
    contact_id INT,
    first_name VARCHAR,
    last_name VARCHAR,
    phone_number VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.contact_id, p.first_name, p.last_name, p.phone_number
    FROM phonebook p
    ORDER BY p.contact_id
    LIMIT limit_count OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;