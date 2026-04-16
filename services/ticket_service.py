from database.db import get_db

class TicketService:
    @staticmethod
    def create_ticket(creator_id, title, problem, category='other'):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO tickets (creator_id, title, problem, category, status) VALUES (%s,%s,%s,%s,'new')",
                (creator_id, title, problem, category)
            )
            ticket_id = cur.lastrowid
            cur.execute(
                "INSERT INTO ticket_history (ticket_id, new_status, changed_by, notes) VALUES (%s,'new',%s,'Ticket created')",
                (ticket_id, creator_id)
            )
            return ticket_id

    @staticmethod
    def get_student_tickets(student_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM tickets WHERE creator_id = %s ORDER BY date_logged DESC", (student_id,))
            return cur.fetchall()

    @staticmethod
    def get_all_tickets():
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""SELECT t.*, u.email as creator_email FROM tickets t
                          JOIN users u ON t.creator_id = u.id ORDER BY t.date_logged DESC""")
            return cur.fetchall()

    @staticmethod
    def get_assigned_tickets(admin_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""SELECT t.*, u.email as creator_email FROM tickets t
                          JOIN users u ON t.creator_id = u.id
                          WHERE t.assigned_admin_id = %s AND t.status IN ('assigned','in-process')
                          ORDER BY t.date_logged DESC""", (admin_id,))
            return cur.fetchall()

    @staticmethod
    def assign_ticket(ticket_id, admin_id, changed_by):
        """Only support can assign tickets, and only 'new' tickets can be assigned."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT role FROM users WHERE id = %s", (changed_by,))
            changer = cur.fetchone()
            if not changer or changer['role'] != 'support':
                return False, "Only support staff can assign tickets."

            cur.execute("SELECT id FROM users WHERE id = %s AND role = 'admin' AND is_active = TRUE", (admin_id,))
            if not cur.fetchone():
                return False, "Please select a valid admin."

            cur.execute("SELECT * FROM tickets WHERE id = %s AND status = 'new'", (ticket_id,))
            ticket = cur.fetchone()
            if not ticket:
                return False, "Ticket not found or not in 'new' status."

            cur.execute("UPDATE tickets SET status = 'assigned', assigned_admin_id = %s WHERE id = %s",
                       (admin_id, ticket_id))
            return True, None

    @staticmethod
    def update_ticket_status(ticket_id, new_status, user_id, solution=None, changed_by=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
            ticket = cur.fetchone()
            if not ticket:
                return False, "Ticket not found."

            cur.execute("SELECT role FROM users WHERE id = %s", (changed_by or user_id,))
            user = cur.fetchone()
            if not user:
                return False, "User not found."

            role = user['role']

            # Enforce: Admin cannot modify 'new' tickets
            if role == 'admin' and ticket['status'] == 'new':
                return False, "Admin cannot modify tickets with status 'new'. Support must assign first."

            # Enforce: Support can only modify 'new' tickets (assign them)
            if role == 'support' and ticket['status'] != 'new':
                return False, "Support can only modify tickets with status 'new'."

            # Valid transitions for admin - FIX: allow assigned->in-process->completed
            valid_transitions = {
                'assigned': ['in-process'],
                'in-process': ['completed'],
            }

            if role == 'admin':
                allowed = valid_transitions.get(ticket['status'], [])
                if new_status not in allowed:
                    return False, f"Cannot transition from '{ticket['status']}' to '{new_status}'."

            update_fields = "status = %s"
            params = [new_status]

            if solution:
                update_fields += ", solution = %s"
                params.append(solution)

            if new_status == 'completed':
                update_fields += ", completion_date = NOW()"

            params.append(ticket_id)
            cur.execute(f"UPDATE tickets SET {update_fields} WHERE id = %s", params)
            return True, None

    @staticmethod
    def get_ticket_history(ticket_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""SELECT th.*, u.email as changed_by_email
                          FROM ticket_history th
                          JOIN users u ON th.changed_by = u.id
                          WHERE th.ticket_id = %s ORDER BY th.changed_at""", (ticket_id,))
            return cur.fetchall()
