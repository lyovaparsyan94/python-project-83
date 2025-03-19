import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseConnection:
    def __init__(self, database_url):
        self.database_url = database_url

    def __enter__(self):
        self.conn = psycopg2.connect(
            self.database_url,
            cursor_factory=RealDictCursor
        )
        with self.conn as conn:
            return conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()


class UrlRepository:
    def __init__(self, database_url):
        self.cursor = DatabaseConnection(database_url)

    def add_url(self, url):
        query = '''
        INSERT INTO urls (name)
        VALUES (%s)
        RETURNING id
        '''
        with self.cursor as cur:
            cur.execute(query, (url,))
            id = cur.fetchone()['id']
            return id

    def find_url(self, url):
        query = '''
        SELECT id, name
        FROM urls
        WHERE name = %s
        '''
        with self.cursor as cur:
            cur.execute(query, (url,))
            url_info = cur.fetchone()
            if not url_info:
                return None
            return url_info

    def find_id(self, id):
        query = '''
        SELECT *
        FROM urls
        WHERE id = %s
        '''
        with self.cursor as cur:
            cur.execute(query, (id,))
            url_info = cur.fetchone()
            if not url_info:
                return None
            return url_info

    def get_all_urls(self):
        query = '''
        SELECT * 
        FROM urls
        ORDER BY id DESC
        '''
        with self.cursor as cur:
            cur.execute(query)
            all_urls = cur.fetchall()
            return all_urls

    def add_url_check(self, data, url_info):
        query = '''
        INSERT INTO url_checks (url_id, status_code, h1, title, description)
        VALUES (%s, %s, %s, %s, %s)
        '''
        with self.cursor as cur:
            cur.execute(query, (
                url_info.get('id'),
                data.get('status'),
                data.get('h1'),
                data.get('title'),
                data.get('description'),
            ))

    def get_url_checks(self, url_id):
        query = '''
        SELECT * 
        FROM url_checks
        WHERE url_id = %s
        ORDER BY id DESC
        '''
        with self.cursor as cur:
            cur.execute(query, (url_id,))
            url_checks_info = cur.fetchall()

            for row in url_checks_info:
                if row['h1'] is None:
                    row['h1'] = ''
                if row['title'] is None:
                    row['title'] = ''
                if row['description'] is None:
                    row['description'] = ''

            return url_checks_info

    def get_all_urls_checks(self):
        query = '''
        SELECT DISTINCT ON (urls.id)
            urls.id AS id, 
            urls.name AS name,
            url_checks.created_at  AS created_at,
            url_checks.status_code AS status_code
        FROM urls
        LEFT JOIN url_checks ON 
            urls.id = url_checks.url_id;
        '''
        with self.cursor as cur:
            cur.execute(query)
            all_urls_checks = cur.fetchall()

            for row in all_urls_checks:
                if row['created_at'] is None:
                    row['created_at'] = ''
                if row['status_code'] is None:
                    row['status_code'] = ''

            return all_urls_checks

