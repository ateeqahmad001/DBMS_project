from database.db import get_db

class StudentProfile:
    @staticmethod
    def get_by_user_id(user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT sp.*, u2.name as uni_name, d.name as dept_name
                FROM student_profiles sp
                LEFT JOIN universities u2 ON sp.university_id = u2.id
                LEFT JOIN departments d ON sp.department_id = d.id
                WHERE sp.user_id = %s""", (user_id,))
            return cur.fetchone()

    @staticmethod
    def create(user_id, data):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO student_profiles (user_id, first_name, last_name, phone, dob, address, university_id, department_id, major, student_status, year)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (user_id, data['first_name'], data['last_name'], data.get('phone'),
                 data.get('dob'), data.get('address'), data.get('university_id') or None,
                 data.get('department_id') or None, data.get('major'),
                 data.get('student_status','UG'), data.get('year'))
            )

    @staticmethod
    def update(user_id, data):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """UPDATE student_profiles SET first_name=%s, last_name=%s, phone=%s,
                dob=%s, address=%s, university_id=%s, department_id=%s, major=%s, student_status=%s, year=%s
                WHERE user_id=%s""",
                (data['first_name'], data['last_name'], data.get('phone'),
                 data.get('dob'), data.get('address'), data.get('university_id') or None,
                 data.get('department_id') or None, data.get('major'),
                 data.get('student_status','UG'), data.get('year'), user_id)
            )
