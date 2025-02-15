import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# users 
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")

# family members
cursor.execute("""
CREATE TABLE IF NOT EXISTS family_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    relation TEXT NOT NULL,
    embedding BLOB NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# medication
cursor.execute("""
CREATE TABLE IF NOT EXISTS medication (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    time TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# stories
cursor.execute("""
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_paths TEXT NOT NULL,
    generated_text TEXT NOT NULL
);
""")


conn.commit()
conn.close()