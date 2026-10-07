import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Retrieve connection details or fall back to defaults
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "6024")
DB_NAME = os.getenv("DB_NAME", "langchain")
DB_USER = os.getenv("DB_USER", "langchain")
DB_PASSWORD = os.getenv("DB_PASSWORD", "langchain")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    print("Successfully connected to PostgreSQL and verified 'vector' extension!")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Database connection error: {e}")