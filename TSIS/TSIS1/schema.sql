-- Create a table for contact groups/categories
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,           -- unique auto-incrementing ID for each group
    name VARCHAR(50) UNIQUE NOT NULL -- group name (Family, Work, etc.) must be unique
);

-- Insert the four default groups into the groups table
INSERT INTO groups (name) VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;       -- if a group already exists, skip it (avoid duplicates)

-- Create the main contacts table with all contact information
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,           -- unique ID for each contact
    name VARCHAR(100) NOT NULL,      -- contact's full name (required)
    phone VARCHAR(20) NOT NULL,      -- primary phone number (required)
    email VARCHAR(100),              -- email address (optional)
    birthday DATE,                   -- birth date (optional)
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL   -- foreign key: which group this contact belongs to; if group is deleted, set to NULL
);

-- Create a separate table for multiple phone numbers per contact
CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,           -- unique ID for each phone record
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,  -- which contact owns this phone; if contact deleted, delete all its phones
    phone VARCHAR(20) NOT NULL,      -- the phone number
    type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))    -- phone type: only home, work, or mobile allowed
);