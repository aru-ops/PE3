-- =========================================
-- PROCEDURES
-- =========================================

-- 1. Insert or update one contact
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM phonebook
        WHERE first_name = p_first_name
          AND COALESCE(last_name, '') = COALESCE(p_last_name, '')
    ) THEN
        UPDATE phonebook
        SET phone_number = p_phone
        WHERE first_name = p_first_name
          AND COALESCE(last_name, '') = COALESCE(p_last_name, '');
    ELSE
        INSERT INTO phonebook(first_name, last_name, phone_number)
        VALUES (p_first_name, p_last_name, p_phone);
    END IF;
END;
$$;


-- 2. Procedure to insert many contacts with validation
-- Incorrect data will be saved into invalid_contacts table
CREATE TABLE IF NOT EXISTS invalid_contacts (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone_number VARCHAR(20),
    error_message TEXT
);

CREATE OR REPLACE PROCEDURE insert_many_contacts(
    first_names TEXT[],
    last_names TEXT[],
    phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
BEGIN
    IF array_length(first_names, 1) IS DISTINCT FROM array_length(last_names, 1)
       OR array_length(first_names, 1) IS DISTINCT FROM array_length(phones, 1) THEN
        RAISE EXCEPTION 'All arrays must have the same length';
    END IF;

    FOR i IN 1..array_length(first_names, 1) LOOP

        IF phones[i] ~ '^\+[0-9]{11,15}$' THEN

            IF EXISTS (
                SELECT 1
                FROM phonebook
                WHERE first_name = first_names[i]
                  AND COALESCE(last_name, '') = COALESCE(last_names[i], '')
            ) THEN
                UPDATE phonebook
                SET phone_number = phones[i]
                WHERE first_name = first_names[i]
                  AND COALESCE(last_name, '') = COALESCE(last_names[i], '');
            ELSE
                INSERT INTO phonebook(first_name, last_name, phone_number)
                VALUES (first_names[i], last_names[i], phones[i]);
            END IF;

        ELSE
            INSERT INTO invalid_contacts(first_name, last_name, phone_number, error_message)
            VALUES (first_names[i], last_names[i], phones[i], 'Invalid phone number');
        END IF;

    END LOOP;
END;
$$;


-- 3. Delete by username or phone
CREATE OR REPLACE PROCEDURE delete_contact(search_value VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE first_name = search_value
       OR last_name = search_value
       OR phone_number = search_value;
END;
$$;