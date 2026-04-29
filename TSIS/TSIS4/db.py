# db.py - Database operations for Snake Game (TSIS 4)
# Manages PostgreSQL connection, player records, game scores, and leaderboard
import psycopg2
import random

# Database connection string (DSN) with parameters:
# host: localhost, port: 5432 (default PostgreSQL), database: postgres,
# user: postgres, password: 12345678 (change to your actual password)
DB_DSN = "host=localhost port=5432 dbname=postgres user=postgres password=12345678"

def get_connection():
    """
    Establish a connection to the PostgreSQL database using the DSN.
    Returns a connection object if successful, or None if an error occurs.
    """
    try:
        return psycopg2.connect(DB_DSN)
    except Exception as e:
        print(f"DB error: {e}")
        return None

def setup_database():
    """
    Create the required tables (players and game_sessions) if they do not exist.
    This function should be called once at the start of the game.
    """
    conn = get_connection()
    if not conn:                         # if connection failed, exit
        return
    cur = conn.cursor()
    # Create players table (stores unique usernames and their IDs)
    cur.execute("CREATE TABLE IF NOT EXISTS players (id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL);")
    # Create game_sessions table (stores each game result linked to a player)
    cur.execute("CREATE TABLE IF NOT EXISTS game_sessions (id SERIAL PRIMARY KEY, player_id INTEGER REFERENCES players(id), score INTEGER NOT NULL, level_reached INTEGER NOT NULL, played_at TIMESTAMP DEFAULT NOW());")
    conn.commit()                        # save changes
    cur.close()
    conn.close()

def get_or_create_player(username):
    """
    Retrieve the player_id for a given username.
    If the username does not exist in the players table, insert it and return the new ID.
    If database connection fails, return a random integer (fallback for testing without DB).
    """
    conn = get_connection()
    if not conn:
        return random.randint(1, 10000)  # fallback ID (game can run without real DB)
    cur = conn.cursor()
    # Try to insert the username; ON CONFLICT does nothing if already exists
    cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT DO NOTHING;", (username,))
    # Now select the ID (whether newly inserted or existing)
    cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
    pid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return pid

def save_score(player_id, score, level):
    """
    Save a completed game session into the game_sessions table.
    Records the player's ID, final score, and the level reached.
    """
    conn = get_connection()
    if not conn:                         # if DB unavailable, silently skip saving
        return
    cur = conn.cursor()
    cur.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s);", (player_id, score, level))
    conn.commit()
    cur.close()
    conn.close()

def get_top_10():
    """
    Retrieve the top 10 highest scores from all players.
    Returns a list of tuples: (username, score, level_reached, played_at_date).
    If DB connection fails, returns an empty list.
    """
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor()
    # Join game_sessions with players to get usernames, order by score descending, limit 10
    cur.execute("SELECT p.username, s.score, s.level_reached, s.played_at::date FROM game_sessions s JOIN players p ON s.player_id = p.id ORDER BY s.score DESC LIMIT 10;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_personal_best(player_id):
    """
    Return the highest score achieved by a specific player.
    Uses COALESCE to return 0 if no sessions exist for that player.
    """
    conn = get_connection()
    if not conn:
        return 0
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(score),0) FROM game_sessions WHERE player_id = %s;", (player_id,))
    best = cur.fetchone()[0]
    cur.close()
    conn.close()
    return best