-- schema.sql
-- 1. Таблица групп
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Начальные группы
INSERT INTO groups (name) VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- 2. Основная таблица контактов (расширенная)
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name  VARCHAR(255),
    email      VARCHAR(100),
    birthday   DATE,
    group_id   INTEGER REFERENCES groups(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(first_name, COALESCE(last_name, '')) -- уникальность по имени+фамилии
);

-- Перенос данных из старой таблицы phonebook (если она существует)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'phonebook') THEN
        INSERT INTO contacts (first_name, last_name)
        SELECT first_name, last_name FROM phonebook
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

-- 3. Таблица телефонов (1 ко многим)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);

-- Перенос старых телефонов (по одному на контакт) из phonebook
DO $$
DECLARE
    old_rec RECORD;
    new_id INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'phonebook') THEN
        FOR old_rec IN SELECT contact_id, first_name, last_name, phone_number FROM phonebook LOOP
            SELECT id INTO new_id FROM contacts 
            WHERE first_name = old_rec.first_name 
              AND COALESCE(last_name,'') = COALESCE(old_rec.last_name,'');
            IF new_id IS NOT NULL AND old_rec.phone_number IS NOT NULL THEN
                INSERT INTO phones (contact_id, phone, type) VALUES (new_id, old_rec.phone_number, 'mobile');
            END IF;
        END LOOP;
    END IF;
END $$;