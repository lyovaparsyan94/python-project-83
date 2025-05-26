import psycopg2
from psycopg2.extras import RealDictCursor


class SiteRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def get_content(self):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls ORDER BY id DESC")
                return cur.fetchall()
    
    def find(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
                row = cur.fetchone()
                return dict(row) if row else None

    def find_by_name(self, name):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
                row = cur.fetchone()
                return dict(row) if row else None
            
    def clear(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'TRUNCATE TABLE urls RESTART IDENTITY CASCADE'
                    )
            conn.commit()
        
    def save(self, url):
        self._create(url)
        return url["id"]

    def _create(self, url):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO urls (name, created_at) 
                    VALUES (%s, CURRENT_DATE)
                    RETURNING id
                    """,
                    (url['url'],)
                )
                id = cur.fetchone()[0]
                url["id"] = id
            conn.commit()
            