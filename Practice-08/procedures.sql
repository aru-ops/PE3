-- This file contains PostgreSQL procedures for the PhoneBook.

-- Procedure 1: Insert or update a contact
-- If the contact exists, update the phone
-- If not, insert a new row
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_name VARCHAR,
    p_surname VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM contacts
        WHERE name = p_name AND surname = p_surname
    ) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE name = p_name AND surname = p_surname;
    ELSE
        INSERT INTO contacts(name, surname, phone)
        VALUES (p_name, p_surname, p_phone);
    END IF;
END;
$$;

-- Procedure 2: Insert many users with phone validation
-- It skips incorrect phone numbers
CREATE OR REPLACE PROCEDURE insert_many_contacts()
LANGUAGE plpgsql
AS $$
DECLARE
    names TEXT[] := ARRAY['Ali', 'Aruzhan', 'Madi', 'Dana'];
    surnames TEXT[] := ARRAY['Khan', 'Sapar', 'Bek', 'Nur'];
    phones TEXT[] := ARRAY['87071234567', '12345', '87778889900', 'abc123'];
    i INT;
BEGIN
    FOR i IN 1..array_length(names, 1) LOOP
        -- Phone must contain only digits and be 11 characters long
        IF phones[i] ~ '^[0-9]{11}$' THEN
            CALL upsert_contact(names[i], surnames[i], phones[i]);
        ELSE
            RAISE NOTICE 'Incorrect data: %, %, %', names[i], surnames[i], phones[i];
        END IF;
    END LOOP;
END;
$$;

-- Procedure 3: Delete contact by name or phone
CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM contacts
    WHERE name = p_value
       OR surname = p_value
       OR phone = p_value;
END;
$$;