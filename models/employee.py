from database.db import get_db

class EmployeeProfile:
    @staticmethod
    def get_by_user_id(user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM employee_profiles WHERE user_id = %s", (user_id,))
            return cur.fetchone()

    @staticmethod
    def create(user_id, data):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO employee_profiles (user_id, employee_id, first_name, last_name, gender, salary, aadhaar, phone, address)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (user_id, data['employee_id'], data['first_name'], data['last_name'],
                 data.get('gender'), data.get('salary'), data.get('aadhaar'),
                 data.get('phone'), data.get('address'))
            )

    @staticmethod
    def get_all():
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""SELECT ep.*, u.email, u.role FROM employee_profiles ep
                          JOIN users u ON ep.user_id = u.id WHERE u.is_active = TRUE""")
            return cur.fetchall()
