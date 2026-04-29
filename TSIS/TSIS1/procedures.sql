-- Procedure to add a phone number to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    c_id INTEGER;
BEGIN
    SELECT id INTO c_id FROM contacts WHERE name = p_contact_name;
    IF c_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    INSERT INTO phones (contact_id, phone, type) VALUES (c_id, p_phone, p_type);
END;
$$;

-- Procedure to move a contact to a group (creates group if it doesn't exist)
CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR, p_group_name VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    c_id INTEGER;
    g_id INTEGER;
BEGIN
    SELECT id INTO c_id FROM contacts WHERE name = p_contact_name;
    IF c_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    SELECT id INTO g_id FROM groups WHERE name = p_group_name;
    IF g_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO g_id;
    END IF;
    UPDATE contacts SET group_id = g_id WHERE id = c_id;
END;
$$;

-- Search function that matches name, phone (any), email
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    contact_id INTEGER,
    name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones_str TEXT
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS group_name,
        string_agg(p.phone || ' (' || p.type || ')', ', ') AS phones_str
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE c.name ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR p.phone ILIKE '%' || p_query || '%'
    GROUP BY c.id, g.name
    ORDER BY c.name;
END;
$$;