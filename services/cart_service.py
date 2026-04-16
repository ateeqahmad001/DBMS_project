from database.db import get_db

class CartService:
    @staticmethod
    def get_or_create_cart(student_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM carts WHERE student_id = %s", (student_id,))
            cart = cur.fetchone()
            if not cart:
                try:
                    cur.execute("INSERT INTO carts (student_id) VALUES (%s)", (student_id,))
                    cur.execute("SELECT * FROM carts WHERE student_id = %s", (student_id,))
                    cart = cur.fetchone()
                except Exception:
                    cur.execute("SELECT * FROM carts WHERE student_id = %s", (student_id,))
                    cart = cur.fetchone()
            return cart

    @staticmethod
    def get_cart_items(student_id):
        db = get_db()
        cart = CartService.get_or_create_cart(student_id)
        with db.cursor() as cur:
            cur.execute("""SELECT ci.*, b.title, b.buy_price, b.rent_price, b.image_url,
                          GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors
                          FROM cart_items ci
                          JOIN books b ON ci.book_id = b.id
                          LEFT JOIN book_authors ba ON b.id = ba.book_id
                          LEFT JOIN authors a ON ba.author_id = a.id
                          WHERE ci.cart_id = %s
                          GROUP BY ci.id""", (cart['id'],))
            return cur.fetchall()

    @staticmethod
    def add_to_cart(student_id, book_id, is_rental=False):
        db = get_db()
        cart = CartService.get_or_create_cart(student_id)
        with db.cursor() as cur:
            cur.execute("SELECT * FROM cart_items WHERE cart_id = %s AND book_id = %s AND is_rental = %s", (cart['id'], book_id, is_rental))
            item = cur.fetchone()
            if item:
                cur.execute("UPDATE cart_items SET quantity = quantity + 1 WHERE id = %s", (item['id'],))
            else:
                cur.execute("INSERT INTO cart_items (cart_id, book_id, quantity, is_rental) VALUES (%s,%s,1,%s)",
                           (cart['id'], book_id, is_rental))

    @staticmethod
    def remove_from_cart(student_id, item_id):
        """If quantity > 1, decrease by 1. If quantity == 1, remove item."""
        db = get_db()
        cart = CartService.get_or_create_cart(student_id)
        with db.cursor() as cur:
            cur.execute("SELECT * FROM cart_items WHERE id = %s AND cart_id = %s", (item_id, cart['id']))
            item = cur.fetchone()
            if not item:
                return
            if item['quantity'] > 1:
                cur.execute("UPDATE cart_items SET quantity = quantity - 1 WHERE id = %s", (item_id,))
            else:
                cur.execute("DELETE FROM cart_items WHERE id = %s AND cart_id = %s", (item_id, cart['id']))

    @staticmethod
    def clear_cart(student_id):
        db = get_db()
        cart = CartService.get_or_create_cart(student_id)
        with db.cursor() as cur:
            cur.execute("DELETE FROM cart_items WHERE cart_id = %s", (cart['id'],))

    @staticmethod
    def get_cart_total(student_id):
        items = CartService.get_cart_items(student_id)
        total = 0
        for item in items:
            price = item['rent_price'] if item['is_rental'] and item['rent_price'] else item['buy_price']
            total += (price or 0) * item['quantity']
        return total
