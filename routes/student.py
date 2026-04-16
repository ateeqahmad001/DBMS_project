from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.decorators import role_required
from utils.validators import validate_phone, validate_name, validate_card_number
from models.book import Book
from models.student import StudentProfile
from services.cart_service import CartService
from services.order_service import OrderService
from services.ticket_service import TicketService
from database.db import get_db
import re

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@role_required('student')
def dashboard():
    profile = StudentProfile.get_by_user_id(session['user_id'])
    orders = OrderService.get_student_orders(session['user_id'])
    tickets = TicketService.get_student_tickets(session['user_id'])
    return render_template('student/dashboard.html', profile=profile, orders=orders[:5], tickets=tickets[:5])

@student_bp.route('/books')
@role_required('student')
def browse_books():
    search = request.args.get('search')
    category_id = request.args.get('category_id')
    books = Book.get_all(search=search, category_id=category_id)
    categories = Book.get_categories()

    profile = StudentProfile.get_by_user_id(session['user_id'])
    course_books_section = []
    if profile and profile.get('department_id'):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT c.id, c.name, c.code, c.year, c.semester
                FROM courses c
                JOIN course_departments cd ON c.id = cd.course_id
                WHERE cd.department_id = %s
                ORDER BY c.name
            """, (profile['department_id'],))
            dept_courses = cur.fetchall()

            for course in dept_courses:
                cur.execute("""
                    SELECT CONCAT(i.first_name, ' ', i.last_name) as name
                    FROM course_instructors ci
                    JOIN instructors i ON ci.instructor_id = i.id
                    WHERE ci.course_id = %s
                """, (course['id'],))
                course['instructors'] = [r['name'] for r in cur.fetchall()]

                cur.execute("""
                    SELECT b.*, cb.link_type, cb.year as cb_year, cb.semester as cb_semester,
                           CONCAT(i.first_name, ' ', i.last_name) as instructor_name,
                           GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors,
                           COALESCE((SELECT AVG(r.rating) FROM reviews r WHERE r.book_id = b.id), 0) as avg_rating
                    FROM course_books cb
                    JOIN books b ON cb.book_id = b.id
                    LEFT JOIN instructors i ON cb.instructor_id = i.id
                    LEFT JOIN book_authors ba ON b.id = ba.book_id
                    LEFT JOIN authors a ON ba.author_id = a.id
                    WHERE cb.course_id = %s
                    GROUP BY cb.id
                    ORDER BY cb.link_type, b.title
                """, (course['id'],))
                course['books'] = cur.fetchall()

                if course['books']:
                    course_books_section.append(course)

    return render_template('student/books.html', books=books, categories=categories,
                          search=search, category_id=category_id,
                          course_books_section=course_books_section, profile=profile)

@student_bp.route('/books/<int:book_id>')
@role_required('student')
def book_detail(book_id):
    book = Book.get_by_id(book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('student.browse_books'))
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT r.*, sp.first_name FROM reviews r JOIN student_profiles sp ON r.student_id = sp.user_id WHERE r.book_id = %s ORDER BY r.created_at DESC", (book_id,))
        reviews = cur.fetchall()
    return render_template('student/book_detail.html', book=book, reviews=reviews)

@student_bp.route('/cart')
@role_required('student')
def view_cart():
    items = CartService.get_cart_items(session['user_id'])
    total = CartService.get_cart_total(session['user_id'])
    return render_template('student/cart.html', items=items, total=total)

@student_bp.route('/cart/add/<int:book_id>', methods=['POST'])
@role_required('student')
def add_to_cart(book_id):
    is_rental = request.form.get('is_rental') == '1'
    try:
        CartService.add_to_cart(session['user_id'], book_id, is_rental)
        flash('Book added to cart!', 'success')
    except Exception:
        flash('Could not add book to cart. Please try again.', 'danger')
    return redirect(request.referrer or url_for('student.browse_books'))

@student_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@role_required('student')
def remove_from_cart(item_id):
    try:
        CartService.remove_from_cart(session['user_id'], item_id)
        flash('Cart updated.', 'info')
    except Exception:
        flash('Could not update cart. Please try again.', 'danger')
    return redirect(url_for('student.view_cart'))

@student_bp.route('/checkout', methods=['GET', 'POST'])
@role_required('student')
def checkout():
    if request.method == 'POST':
        # Validate card number
        card_number = request.form.get('credit_card_number', '').strip()
        card_valid, card_err = validate_card_number(card_number)
        if not card_valid:
            flash(card_err, 'danger')
            return redirect(url_for('student.checkout'))

        card_holder = request.form.get('card_holder_name', '').strip()
        name_valid, name_err = validate_name(card_holder, "Card holder name")
        if not name_valid:
            flash(name_err, 'danger')
            return redirect(url_for('student.checkout'))

        expiry = request.form.get('expiry_date', '').strip()
        if not re.match(r'^\d{2}/\d{2}$', expiry):
            flash('Expiry date must be in MM/YY format.', 'danger')
            return redirect(url_for('student.checkout'))

        shipping_address = request.form.get('shipping_address', '').strip()
        if not shipping_address:
            flash('Shipping address is required.', 'danger')
            return redirect(url_for('student.checkout'))

        order_id, error = OrderService.create_order(
            session['user_id'],
            request.form.get('shipping_type', 'standard'),
            shipping_address,
            re.sub(r'[\s\-]', '', card_number),
            expiry,
            card_holder,
            request.form.get('card_type', '')
        )
        if error:
            flash(error, 'danger')
            return redirect(url_for('student.view_cart'))
        flash(f'Order #{order_id} placed successfully!', 'success')
        return redirect(url_for('student.orders'))
    items = CartService.get_cart_items(session['user_id'])
    total = CartService.get_cart_total(session['user_id'])
    profile = StudentProfile.get_by_user_id(session['user_id'])
    return render_template('student/checkout.html', items=items, total=total, profile=profile)

@student_bp.route('/orders')
@role_required('student')
def orders():
    all_orders = OrderService.get_student_orders(session['user_id'])
    return render_template('student/orders.html', orders=all_orders)

@student_bp.route('/orders/<int:order_id>')
@role_required('student')
def order_detail(order_id):
    order = OrderService.get_order_details(order_id)
    if not order or order['student_id'] != session['user_id']:
        flash('Order not found.', 'danger')
        return redirect(url_for('student.orders'))
    return render_template('student/order_detail.html', order=order)

@student_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@role_required('student')
def cancel_order(order_id):
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Please provide a reason for cancellation.', 'danger')
        return redirect(url_for('student.order_detail', order_id=order_id))
    success, error = OrderService.request_cancellation(order_id, session['user_id'], reason)
    if success:
        flash('Cancellation request submitted. Awaiting support approval.', 'info')
    else:
        flash(error or 'Cannot cancel this order.', 'danger')
    return redirect(url_for('student.order_detail', order_id=order_id))

@student_bp.route('/orders/<int:order_id>/review/<int:book_id>', methods=['POST'])
@role_required('student')
def review_book(order_id, book_id):
    order = OrderService.get_order_details(order_id)
    if not order or order['student_id'] != session['user_id'] or order['order_status'] != 'completed':
        flash('You can only review books from completed orders.', 'danger')
        return redirect(url_for('student.orders'))
    rating = int(request.form.get('rating', 3))
    review_text = request.form.get('review_text', '')
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM reviews WHERE book_id=%s AND student_id=%s AND order_id=%s",
                   (book_id, session['user_id'], order_id))
        if cur.fetchone():
            flash('You already reviewed this book for this order.', 'warning')
        else:
            try:
                cur.execute("INSERT INTO reviews (book_id, student_id, order_id, rating, review_text) VALUES (%s,%s,%s,%s,%s)",
                           (book_id, session['user_id'], order_id, rating, review_text))
                flash('Review submitted!', 'success')
            except Exception:
                flash('Could not submit review. Please try again.', 'danger')
    return redirect(url_for('student.order_detail', order_id=order_id))

@student_bp.route('/tickets')
@role_required('student')
def tickets():
    all_tickets = TicketService.get_student_tickets(session['user_id'])
    return render_template('student/tickets.html', tickets=all_tickets)

@student_bp.route('/tickets/create', methods=['GET', 'POST'])
@role_required('student')
def create_ticket():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        problem = request.form.get('problem', '').strip()
        category = request.form.get('category', 'other')
        if not title or not problem:
            flash('Title and problem are required.', 'danger')
            return render_template('student/create_ticket.html')
        try:
            TicketService.create_ticket(session['user_id'], title, problem, category)
            flash('Ticket created successfully.', 'success')
            return redirect(url_for('student.tickets'))
        except Exception:
            flash('Could not create ticket. Please try again.', 'danger')
            return render_template('student/create_ticket.html')
    return render_template('student/create_ticket.html')

@student_bp.route('/profile', methods=['GET', 'POST'])
@role_required('student')
def profile():
    db = get_db()
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        fn_valid, fn_err = validate_name(first_name, "First name")
        if not fn_valid:
            flash(fn_err, 'danger')
            return redirect(url_for('student.profile'))
        ln_valid, ln_err = validate_name(last_name, "Last name")
        if not ln_valid:
            flash(ln_err, 'danger')
            return redirect(url_for('student.profile'))

        phone = request.form.get('phone', '').strip()
        ph_valid, ph_err = validate_phone(phone)
        if not ph_valid:
            flash(ph_err, 'danger')
            return redirect(url_for('student.profile'))

        try:
            StudentProfile.update(session['user_id'], {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone or None,
                'dob': request.form.get('dob') or None,
                'address': request.form.get('address'),
                'university_id': request.form.get('university_id') or None,
                'department_id': request.form.get('department_id') or None,
                'major': request.form.get('major'),
                'student_status': request.form.get('student_status', 'UG'),
                'year': request.form.get('year') or None
            })
            flash('Profile updated!', 'success')
        except Exception:
            flash('Could not update profile. Please try again.', 'danger')
        return redirect(url_for('student.profile'))

    prof = StudentProfile.get_by_user_id(session['user_id'])
    with db.cursor() as cur:
        cur.execute("SELECT * FROM universities ORDER BY name")
        unis = cur.fetchall()
        departments = []
        if prof and prof.get('university_id'):
            cur.execute("SELECT * FROM departments WHERE university_id = %s ORDER BY name", (prof['university_id'],))
            departments = cur.fetchall()
    return render_template('student/profile.html', profile=prof, universities=unis, departments=departments)

@student_bp.route('/delete-account', methods=['POST'])
@role_required('student')
def delete_account():
    user_id = session['user_id']
    db = get_db()
    try:
        db.autocommit(False)
        with db.cursor() as cur:
            # Delete related data
            cur.execute("DELETE FROM reviews WHERE student_id = %s", (user_id,))
            cur.execute("DELETE FROM cart_items WHERE cart_id IN (SELECT id FROM carts WHERE student_id = %s)", (user_id,))
            cur.execute("DELETE FROM carts WHERE student_id = %s", (user_id,))
            cur.execute("DELETE FROM tickets WHERE creator_id = %s", (user_id,))
            cur.execute("DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE student_id = %s)", (user_id,))
            cur.execute("DELETE FROM orders WHERE student_id = %s", (user_id,))
            cur.execute("DELETE FROM student_profiles WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        session.clear()
        flash('Your account has been permanently deleted.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.rollback()
        flash('Could not delete account. Please try again or contact support.', 'danger')
        return redirect(url_for('student.profile'))
    finally:
        db.autocommit(True)
