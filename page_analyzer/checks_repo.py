import psycopg2
from psycopg2.extras import RealDictCursor


class CheckRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def get_content_by_url_id(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM url_checks " 
                "WHERE url_id = %s ORDER BY id DESC", (id,))
                return cur.fetchall()
            
    def get_last_check_date_by_id(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT created_at FROM url_checks " 
                "WHERE url_id = %s ORDER BY id DESC", (id,))
                raw_row = cur.fetchone()
                last_check = raw_row['created_at'] if raw_row else ''
                return last_check
            
    def get_last_status_code_by_id(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT status_code FROM url_checks " 
                "WHERE url_id = %s ORDER BY id DESC", (id,))
                raw_row = cur.fetchone()
                last_status_code = raw_row['status_code'] if raw_row else ''
                return last_status_code

    def clear(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'TRUNCATE TABLE url_checks RESTART IDENTITY'
                    )
            conn.commit()

    def save(self, url_id, status_code=0, h1='', title='', desc=''):
        self._create(url_id, status_code, h1, title, desc)

    def _create(self, url_id, status_code, h1, title, desc):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO url_checks (url_id, status_code, h1,
                    title, description, created_at) 
                    VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
                    RETURNING id
                    """,
                    (url_id, status_code, h1, title, desc)
                )
                # id = cur.fetchone()[0]
            conn.commit()
            
    
            
    