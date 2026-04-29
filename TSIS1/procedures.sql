-- procedures.sql

-- 2.1 Добавить телефон существующему контакту (по имени+фамилии)
CREATE OR REPLACE PROCEDURE add_phone(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id FROM contacts
    WHERE first_name = p_first_name AND COALESCE(last_name,'') = COALESCE(p_last_name,'');
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact "% %" not found', p_first_name, p_last_name;
    END IF;
    INSERT INTO phones (contact_id, phone, type) VALUES (v_contact_id, p_phone, p_type);
END;
$$;

-- 2.2 Переместить контакт в другую группу (создать группу, если не существует)
CREATE OR REPLACE PROCEDURE move_to_group(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id INTEGER;
BEGIN
    -- вставить группу, если её нет
    INSERT INTO groups (name) VALUES (p_group_name) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    -- обновить контакт
    UPDATE contacts SET group_id = v_group_id
    WHERE first_name = p_first_name AND COALESCE(last_name,'') = COALESCE(p_last_name,'');
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact "% %" not found', p_first_name, p_last_name;
    END IF;
END;
$$;

-- 2.3 Расширенный поиск: по имени, фамилии, email, любому телефону
CREATE OR REPLACE FUNCTION search_contacts_enhanced(p_query TEXT)
RETURNS TABLE(
    id INTEGER,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT
)
LANGUAGE sql AS $$
    SELECT DISTINCT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name AS group_name,
        (SELECT string_agg(phone || ' (' || type || ')', ', ') FROM phones WHERE contact_id = c.id) AS phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    WHERE c.first_name ILIKE '%' || p_query || '%'
       OR c.last_name  ILIKE '%' || p_query || '%'
       OR c.email      ILIKE '%' || p_query || '%'
       OR EXISTS (SELECT 1 FROM phones p WHERE p.contact_id = c.id AND p.phone ILIKE '%' || p_query || '%')
    ORDER BY c.first_name, c.last_name;
$$;

-- 2.4 Пагинация с сортировкой (заменяет старую get_contacts_paginated)
CREATE OR REPLACE FUNCTION paginate_contacts_ext(
    p_limit INT,
    p_offset INT,
    p_sort_by TEXT DEFAULT 'first_name',
    p_order TEXT DEFAULT 'ASC'
)
RETURNS TABLE(
    id INTEGER,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    created_at TIMESTAMP,
    phones TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_sort_by NOT IN ('first_name', 'birthday', 'created_at') THEN
        RAISE EXCEPTION 'Invalid sort column. Allowed: first_name, birthday, created_at';
    END IF;
    IF upper(p_order) NOT IN ('ASC', 'DESC') THEN
        RAISE EXCEPTION 'Invalid order. Use ASC or DESC';
    END IF;
    RETURN QUERY EXECUTE format('
        SELECT 
            c.id, c.first_name, c.last_name, c.email, c.birthday,
            g.name AS group_name, c.created_at,
            (SELECT string_agg(phone || '' ('' || type || '')'', '', '') FROM phones WHERE contact_id = c.id) AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY %I %s
        LIMIT %L OFFSET %L',
        p_sort_by, p_order, p_limit, p_offset
    );
END;
$$;