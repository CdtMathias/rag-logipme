import psycopg2
import os
import json

conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT")
)
cursor = conn.cursor()

def save_document(doc_name, chunk, embedding):
    cursor.execute("INSERT INTO documents (doc_name, chunk, embedding) VALUES (%s, %s, %s)", (doc_name, chunk, embedding))
    conn.commit()

def search_chunks(query_embedding, top_k):
    import json
    vector_str = json.dumps(query_embedding)
    cursor.execute(
        "SELECT chunk FROM documents ORDER BY embedding <=> %s::vector LIMIT %s",
        (vector_str, top_k)
    )
    return cursor.fetchall()

# USER #

def create_user(username, hashed_password):
    try:
        cursor.execute("INSERT INTO users (username, hashed_password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def get_user(username):
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    return cursor.fetchone()

# CONVERSATION # 

def load_conversation_by_user_id(user_id):
    try:
        cursor.execute("SELECT role, content FROM conversations WHERE user_id = %s ORDER BY created_at", (user_id,))
        rows = cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in rows]
    except Exception:
        conn.rollback()
        raise

def save_message(user_id, role, content):
    try:
        cursor.execute("INSERT INTO conversations (user_id, role, content) VALUES (%s, %s, %s)", (user_id, role, content))
        conn.commit()
    except Exception:
        conn.rollback()
        raise