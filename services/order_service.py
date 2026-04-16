import threading
import logging
from database.db import get_db
from services.cart_service import CartService

logger = logging.getLogger(__name__)

# Delivery type to auto-complete delay mapping (in seconds)
DELIVERY_DELAYS = {
    '1-day': 10,
    '2-day': 20,
    'standard': 30,
}


def _auto_complete_order(app, order_id, delay):
    """Background thread that auto-completes an order after a delay,
    unless the order has been cancelled or cancel_requested in the meantime."""
    import time
    time.sleep(delay)
    try:
        with app.app_context():
            db = get_db()
            with db.cursor() as cur:
                # Only complete if status is still 'new' — avoids race with cancellation
                cur.execute(
                    "UPDATE orders SET order_status = 'completed' WHERE id = %s AND order_status = 'new'",
                    (order_id,)
                )
                if cur.rowcount > 0:
                    logger.info(f"Order #{order_id} auto-completed after {delay}s delay")
                else:
                    logger.info(f"Order #{order_id} was not auto-completed (status changed)")
    except Exception as e:
        logger.error(f"Error auto-completing order #{order_id}: {e}")


class OrderService:
    @staticmethod
    def create_order(student_id, shipping_type, shipping_address, credit_card_number, expiry_date, card_holder_name, card_type):
        items = CartService.get_cart_items(student_id)
        if not items:
            return None, "Cart is empty"
        total = CartService.get_cart_total(student_id)
        db = get_db()
        try:
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO orders (student_id, shipping_type, shipping_address,
                    credit_card_number, expiry_date, card_holder_name, card_type,
                    payment_status, total_amount, order_status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,'paid',%s,'new')""",
                    (student_id, shipping_type, shipping_address,
                     credit_card_number, expiry_date, card_holder_name, card_type or None,
                     total)
                )
                order_id = cur.lastrowid
                for item in items:
                    price = item['rent_price'] if item['is_rental'] and item['rent_price'] else item['buy_price']
                    cur.execute(
                        "INSERT INTO order_items (order_id, book_id, quantity, price, is_rental) VALUES (%s,%s,%s,%s,%s)",
                        (order_id, item['book_id'], item['quantity'], price, item['is_rental'])
                    )
                CartService.clear_cart(student_id)

                # Schedule auto-completion based on shipping type
                delay = DELIVERY_DELAYS.get(shipping_type, 30)
                from flask import current_app
                app = current_app._get_current_object()
                t = threading.Thread(target=_auto_complete_order, args=(app, order_id, delay), daemon=True)
                t.start()
                logger.info(f"Order #{order_id} created. Auto-complete scheduled in {delay}s (shipping: {shipping_type})")

                return order_id, None
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None, "An error occurred while placing your order. Please try again."

    @staticmethod
    def get_student_orders(student_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM orders WHERE student_id = %s ORDER BY order_date DESC", (student_id,))
            return cur.fetchall()

    @staticmethod
    def get_order_details(order_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = cur.fetchone()
            if order:
                cur.execute("""SELECT oi.*, b.title, b.image_url,
                              GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors
                              FROM order_items oi
                              JOIN books b ON oi.book_id = b.id
                              LEFT JOIN book_authors ba ON b.id = ba.book_id
                              LEFT JOIN authors a ON ba.author_id = a.id
                              WHERE oi.order_id = %s
                              GROUP BY oi.id""", (order_id,))
                order['items'] = cur.fetchall()
                cur.execute("SELECT * FROM order_cancellations WHERE order_id = %s ORDER BY requested_at DESC LIMIT 1", (order_id,))
                order['cancellation'] = cur.fetchone()
            return order

    @staticmethod
    def request_cancellation(order_id, student_id, reason):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM orders WHERE id = %s AND student_id = %s", (order_id, student_id))
            order = cur.fetchone()
            if not order:
                return False, "Order not found"
            if order['order_status'] in ('cancelled', 'cancel_requested', 'completed'):
                return False, "Cannot cancel this order"
            cur.execute("SELECT id, decision FROM order_cancellations WHERE order_id = %s", (order_id,))
            existing = cur.fetchone()
            if existing:
                if existing['decision'] == 'rejected':
                    return False, "Your cancellation request was previously rejected. You cannot request again."
                return False, "Cancellation already requested"
            cur.execute(
                "INSERT INTO order_cancellations (order_id, reason, original_status) VALUES (%s, %s, %s)",
                (order_id, reason, order['order_status'])
            )
            cur.execute("UPDATE orders SET order_status = 'cancel_requested' WHERE id = %s", (order_id,))
            return True, None

    @staticmethod
    def approve_cancellation(order_id, support_user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE order_cancellations SET decision = 'approved', approved_by = %s, decided_at = NOW() WHERE order_id = %s AND decision = 'pending'",
                (support_user_id, order_id)
            )
            if cur.rowcount == 0:
                return False
            cur.execute("UPDATE orders SET order_status = 'cancelled' WHERE id = %s", (order_id,))
            return True

    @staticmethod
    def reject_cancellation(order_id, support_user_id):
        """When support rejects cancellation, set order status to 'completed'."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT original_status FROM order_cancellations WHERE order_id = %s AND decision = 'pending'", (order_id,))
            row = cur.fetchone()
            if not row:
                return False
            cur.execute(
                "UPDATE order_cancellations SET decision = 'rejected', approved_by = %s, decided_at = NOW() WHERE order_id = %s AND decision = 'pending'",
                (support_user_id, order_id)
            )
            # Per requirement: if support rejects → status becomes 'completed'
            cur.execute("UPDATE orders SET order_status = 'completed' WHERE id = %s", (order_id,))
            return True

    @staticmethod
    def get_all_orders():
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""SELECT o.*, u.email, sp.first_name, sp.last_name FROM orders o
                          JOIN users u ON o.student_id = u.id
                          LEFT JOIN student_profiles sp ON o.student_id = sp.user_id
                          ORDER BY o.order_date DESC""")
            return cur.fetchall()

    @staticmethod
    def get_cancellation_requests():
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""SELECT o.*, u.email, sp.first_name, sp.last_name, oc.reason, oc.requested_at, oc.decision
                          FROM orders o
                          JOIN users u ON o.student_id = u.id
                          LEFT JOIN student_profiles sp ON o.student_id = sp.user_id
                          JOIN order_cancellations oc ON o.id = oc.order_id
                          WHERE oc.decision = 'pending'
                          ORDER BY oc.requested_at DESC""")
            return cur.fetchall()
