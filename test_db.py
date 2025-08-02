import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

print("DATABASE_URL from .env:", os.getenv('DATABASE_URL'))

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    cur.execute('SELECT * FROM urls')
    print("URLs table:", cur.fetchall())
    
    cur.execute('SELECT * FROM url_checks')
    print("URL checks table:", cur.fetchall())
    
    cur.close()
    conn.close()
    print("Database connection successful!")
except Exception as e:
    print(f"Database connection error: {str(e)}")