from database.db import get_db
import bcrypt
import logging

logger = logging.getLogger(__name__)

class User:
    @staticmethod
    def find_by_email(email):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            return user

    @staticmethod
    def verify_password(plain_password, hashed_password):
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"[AUTH] verify_password error: {e}")
            return False

    @staticmethod
    def _hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def create_user(email, password, role):
        db = get_db()
        hashed = User._hash_password(password)
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
                (email, hashed, role)
            )
            return cur.lastrowid

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cur.fetchone()

    @staticmethod
    def get_all_by_role(role):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE role = %s AND is_active = TRUE", (role,))
            return cur.fetchall()
