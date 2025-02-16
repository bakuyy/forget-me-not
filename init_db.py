import sqlite3

def drop_tables():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # drop tables at the start
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("DROP TABLE IF EXISTS medication;")
    cursor.execute("DROP TABLE IF EXISTS stories;")
    cursor.execute("DROP TABLE IF EXISTS members;")
    
    conn.commit()
    conn.close()

drop_tables()

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

# medication
cursor.execute("""
CREATE TABLE IF NOT EXISTS medication (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    frequency TEXT NOT NULL,
);
""")

# stories
cursor.execute("""
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# members
cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    relation TEXT NOT NULL,
    favourite_memory TEXT NOT NULL
);
""")
conn.commit()
conn.close()