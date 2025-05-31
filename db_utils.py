import sqlite3

DB_PATH = 'scheduler.db'

def get_all(table):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table}")
    data = c.fetchall()
    columns = [desc[0] for desc in c.description]
    conn.close()
    return [dict(zip(columns, row)) for row in data]

def execute_sql(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(sql, params)
    conn.commit()
    conn.close()

def query_sql(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(sql, params)
    data = c.fetchall()
    columns = [desc[0] for desc in c.description]
    conn.close()
    return [dict(zip(columns, row)) for row in data]
