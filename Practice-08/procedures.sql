-- PROCEDURES

-- 1. Insert or update one contact
CREATE OR REPLACE PROCEDURE upsert_contact(  -- update if it exists + insert if not
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if contact already exists
    IF EXISTS (
        SELECT 1
        FROM phonebook
        WHERE first_name = p_first_name
          AND COALESCE(last_name, '') = COALESCE(p_last_name, '') -- coalesce(x,y) if x=null then get y
    ) THEN
        -- Update phone if contact exists
        UPDATE phonebook
        SET phone_number = p_phone
        WHERE first_name = p_first_name
          AND COALESCE(last_name, '') = COALESCE(p_last_name, '');
    ELSE
        -- Insert new contact if not found
        INSERT INTO phonebook(first_name, last_name, phone_number)
        VALUES (p_first_name, p_last_name, p_phone);
    END IF;
END;
$$;


-- 2. Table for invalid contacts
CREATE TABLE IF NOT EXISTS invalid_contacts (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone_number VARCHAR(20),
    error_message TEXT
);


-- 3. Insert many contacts with validation
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    first_names TEXT[],
    last_names TEXT[],
    phones TEXT[]  -- accepts arrays for inserting multiple contacts at once
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;   -- Loop counter
BEGIN
    -- Check that all arrays have the same size
    IF array_length(first_names, 1) IS DISTINCT FROM array_length(last_names, 1)
       OR array_length(first_names, 1) IS DISTINCT FROM array_length(phones, 1) THEN
        RAISE EXCEPTION 'All arrays must have the same length';   -- check that all arrays have the same length before processing them
    END IF;

    -- Loop through all contacts
    FOR i IN 1..array_length(first_names, 1) LOOP

        -- Validate phone format: + and 11-15 digits
        IF phones[i] ~ '^\+[0-9]{11,15}$' THEN

            -- If contact exists, update phone
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
                -- Insert new valid contact
                INSERT INTO phonebook(first_name, last_name, phone_number)
                VALUES (first_names[i], last_names[i], phones[i]);
            END IF;

        ELSE
            -- Save invalid contact separately
            INSERT INTO invalid_contacts(first_name, last_name, phone_number, error_message)
            VALUES (first_names[i], last_names[i], phones[i], 'Invalid phone number');
        END IF;

    END LOOP;
END;
$$;


-- 4. Delete contact by name, surname, or phone
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
