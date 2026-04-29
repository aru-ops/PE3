import psycopg2
import random

DB_DSN = "host=localhost port=5432 dbname=postgres user=postgres password=12345678"

def get_connection():
    try:
        return psycopg2.connect(DB_DSN)
    except Exception as e:
        print(f"DB error: {e}")
        return None

def setup_database():
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS players (id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL);")
    cur.execute("CREATE TABLE IF NOT EXISTS game_sessions (id SERIAL PRIMARY KEY, player_id INTEGER REFERENCES players(id), score INTEGER NOT NULL, level_reached INTEGER NOT NULL, played_at TIMESTAMP DEFAULT NOW());")
    conn.commit()
    cur.close()
    conn.close()

def get_or_create_player(username):
    conn = get_connection()
    if not conn: return random.randint(1,10000)
    cur = conn.cursor()
    cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT DO NOTHING;", (username,))
    cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
    pid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return pid

def save_score(player_id, score, level):
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    cur.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s);", (player_id, score, level))
    conn.commit()
    cur.close()
    conn.close()

def get_top_10():
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor()
    cur.execute("SELECT p.username, s.score, s.level_reached, s.played_at::date FROM game_sessions s JOIN players p ON s.player_id = p.id ORDER BY s.score DESC LIMIT 10;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_personal_best(player_id):
    conn = get_connection()
    if not conn: return 0
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(score),0) FROM game_sessions WHERE player_id = %s;", (player_id,))
    best = cur.fetchone()[0]
    cur.close()
    conn.close()
    return best