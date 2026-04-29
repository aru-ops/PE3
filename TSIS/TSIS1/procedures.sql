-- Procedure to add a phone number to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$   -- use PL/pgSQL language
DECLARE
    c_id INTEGER;        -- variable to store the contact's id
BEGIN
    -- Try to find the contact by name
    SELECT id INTO c_id FROM contacts WHERE name = p_contact_name;
    -- If no contact found, raise an error
    IF c_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    -- Insert the new phone into the phones table (linked to the found contact)
    INSERT INTO phones (contact_id, phone, type) VALUES (c_id, p_phone, p_type);
END;
$$;

-- Procedure to move a contact to a group (creates group if it doesn't exist)
CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR, p_group_name VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    c_id INTEGER;        -- contact id
    g_id INTEGER;        -- group id
BEGIN
    -- Find the contact by name
    SELECT id INTO c_id FROM contacts WHERE name = p_contact_name;
    IF c_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    -- Try to find the group by name
    SELECT id INTO g_id FROM groups WHERE name = p_group_name;
    -- If group does not exist, create it automatically
    IF g_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO g_id;
    END IF;
    -- Update the contact's group_id to the new group
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
    -- Return a query result set
    RETURN QUERY
    SELECT DISTINCT
        c.id,                              -- contact id
        c.name,                            -- contact name
        c.email,                           -- email address
        c.birthday,                        -- birthday date
        g.name AS group_name,              -- group name (or NULL if no group)
        string_agg(p.phone || ' (' || p.type || ')', ', ') AS phones_str  -- concatenate all phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id          -- join groups (may be NULL)
    LEFT JOIN phones p ON c.id = p.contact_id       -- join phones (may be multiple)
    WHERE 
        c.name ILIKE '%' || p_query || '%'          -- partial match on name (case-insensitive)
        OR c.email ILIKE '%' || p_query || '%'      -- partial match on email
        OR p.phone ILIKE '%' || p_query || '%'      -- partial match on any phone number
    GROUP BY c.id, g.name                           -- group by contact to aggregate phones
    ORDER BY c.name;                                -- sort alphabetical by name
END;
$$;