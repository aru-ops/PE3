-- This file contains PostgreSQL functions for the PhoneBook.

-- Create table first if it does not exist
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    surname VARCHAR(100),
    phone VARCHAR(20)
);

-- Function 1: Search contacts by pattern
-- It searches in name, surname, and phone
CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern TEXT)
RETURNS TABLE(id INT, name VARCHAR, surname VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.surname, c.phone
    FROM contacts c
    WHERE c.name ILIKE '%' || p_pattern || '%'
       OR c.surname ILIKE '%' || p_pattern || '%'
       OR c.phone ILIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;

-- Function 2: Get contacts with pagination
-- LIMIT = how many rows to show
-- OFFSET = how many rows to skip
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, name VARCHAR, surname VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.surname, c.phone
    FROM contacts c
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;