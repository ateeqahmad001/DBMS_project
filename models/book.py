from database.db import get_db

class Book:
    @staticmethod
    def get_all(search=None, category_id=None):
        db = get_db()
        with db.cursor() as cur:
            query = """SELECT b.*, c.name as category_name,
                       GROUP_CONCAT(DISTINCT a.name ORDER BY a.name SEPARATOR ', ') as authors,
                       GROUP_CONCAT(DISTINCT k.name ORDER BY k.name SEPARATOR ', ') as keywords,
                       COALESCE((SELECT AVG(r.rating) FROM reviews r WHERE r.book_id = b.id), 0) as avg_rating
                       FROM books b
                       JOIN categories c ON b.category_id = c.id
                       LEFT JOIN book_authors ba ON b.id = ba.book_id
                       LEFT JOIN authors a ON ba.author_id = a.id
                       LEFT JOIN book_keywords bk ON b.id = bk.book_id
                       LEFT JOIN keywords k ON bk.keyword_id = k.id
                       WHERE 1=1"""
            params = []
            if search:
                query += " AND (b.title LIKE %s OR a.name LIKE %s OR k.name LIKE %s OR b.isbn LIKE %s)"
                s = f"%{search}%"
                params.extend([s, s, s, s])
            if category_id:
                query += " AND b.category_id = %s"
                params.append(category_id)
            query += " GROUP BY b.id ORDER BY b.created_at DESC"
            cur.execute(query, params)
            return cur.fetchall()

    @staticmethod
    def get_by_id(book_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""SELECT b.*, c.name as category_name,
                           GROUP_CONCAT(DISTINCT a.name ORDER BY a.name SEPARATOR ', ') as authors,
                           GROUP_CONCAT(DISTINCT k.name ORDER BY k.name SEPARATOR ', ') as keywords,
                           COALESCE((SELECT AVG(r.rating) FROM reviews r WHERE r.book_id = b.id), 0) as avg_rating
                           FROM books b
                           JOIN categories c ON b.category_id = c.id
                           LEFT JOIN book_authors ba ON b.id = ba.book_id
                           LEFT JOIN authors a ON ba.author_id = a.id
                           LEFT JOIN book_keywords bk ON b.id = bk.book_id
                           LEFT JOIN keywords k ON bk.keyword_id = k.id
                           WHERE b.id = %s
                           GROUP BY b.id""", (book_id,))
            return cur.fetchone()

    @staticmethod
    def _sync_authors(cur, book_id, authors_str):
        """Sync authors for a book from comma-separated string."""
        cur.execute("DELETE FROM book_authors WHERE book_id = %s", (book_id,))
        if not authors_str:
            return
        for name in [n.strip() for n in authors_str.split(',') if n.strip()]:
            cur.execute("INSERT IGNORE INTO authors (name) VALUES (%s)", (name,))
            cur.execute("SELECT id FROM authors WHERE name = %s", (name,))
            author_id = cur.fetchone()['id']
            cur.execute("INSERT IGNORE INTO book_authors (book_id, author_id) VALUES (%s, %s)", (book_id, author_id))

    @staticmethod
    def _sync_keywords(cur, book_id, keywords_str):
        """Sync keywords for a book from comma-separated string."""
        cur.execute("DELETE FROM book_keywords WHERE book_id = %s", (book_id,))
        if not keywords_str:
            return
        for name in [n.strip() for n in keywords_str.split(',') if n.strip()]:
            cur.execute("INSERT IGNORE INTO keywords (name) VALUES (%s)", (name,))
            cur.execute("SELECT id FROM keywords WHERE name = %s", (name,))
            kw_id = cur.fetchone()['id']
            cur.execute("INSERT IGNORE INTO book_keywords (book_id, keyword_id) VALUES (%s, %s)", (book_id, kw_id))

    @staticmethod
    def create(data):
        db = get_db()
        with db.cursor() as cur:
            # Check for duplicate ISBN
            isbn = data.get('isbn')
            if isbn:
                isbn = isbn.strip()
                cur.execute("SELECT id FROM books WHERE isbn = %s", (isbn,))
                if cur.fetchone():
                    raise ValueError("A book with this ISBN already exists.")
            cur.execute(
                """INSERT INTO books (title, isbn, publisher, publication_date, edition,
                language, format, book_type, purchase_option, buy_price, rent_price, quantity, category_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (data['title'], data.get('isbn') or None, data.get('publisher'),
                 data.get('publication_date'), data.get('edition'), data.get('language', 'English'),
                 data.get('format', 'paperback'), data.get('book_type', 'new'), data.get('purchase_option', 'buy'),
                 data.get('buy_price'), data.get('rent_price'), data.get('quantity', 0),
                 data['category_id'])
            )
            book_id = cur.lastrowid
            Book._sync_authors(cur, book_id, data.get('authors', ''))
            Book._sync_keywords(cur, book_id, data.get('keywords', ''))
        db.commit()
        return book_id

    @staticmethod
    def update(book_id, data):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """UPDATE books SET title=%s, isbn=%s, publisher=%s,
                publication_date=%s, edition=%s, language=%s, format=%s, book_type=%s,
                purchase_option=%s, buy_price=%s, rent_price=%s, quantity=%s,
                category_id=%s WHERE id=%s""",
                (data['title'], data.get('isbn') or None, data.get('publisher'),
                 data.get('publication_date'), data.get('edition'), data.get('language', 'English'),
                 data.get('format', 'paperback'), data.get('book_type', 'new'), data.get('purchase_option', 'buy'),
                 data.get('buy_price'), data.get('rent_price'), data.get('quantity', 0),
                 data['category_id'], book_id)
            )
            Book._sync_authors(cur, book_id, data.get('authors', ''))
            Book._sync_keywords(cur, book_id, data.get('keywords', ''))
        db.commit()

    @staticmethod
    def delete(book_id):
        db = get_db()
        with db.cursor() as cur:
            # CASCADE handles book_authors, book_keywords, course_books, cart_items, reviews, order_items
            cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
        db.commit()

    @staticmethod
    def get_categories():
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM categories ORDER BY name")
            return cur.fetchall()
