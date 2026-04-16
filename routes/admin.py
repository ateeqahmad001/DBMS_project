from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.decorators import role_required
from utils.validators import validate_price, validate_quantity, validate_name, validate_phone, validate_email
from models.book import Book
from models.employee import EmployeeProfile
from services.ticket_service import TicketService
from database.db import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    tickets = TicketService.get_assigned_tickets(session['user_id'])
    books = Book.get_all()
    return render_template('admin/dashboard.html', tickets=tickets, books=books[:10])

@admin_bp.route('/books')
@role_required('admin')
def manage_books():
    books = Book.get_all()
    return render_template('admin/books.html', books=books)

@admin_bp.route('/books/add', methods=['GET', 'POST'])
@role_required('admin')
def add_book():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        t_valid, t_err = validate_name(title, "Title")
        if not t_valid:
            flash(t_err, 'danger')
            return redirect(url_for('admin.add_book'))

        bp_valid, bp_err = validate_price(request.form.get('buy_price'), "Buy price")
        if not bp_valid:
            flash(bp_err, 'danger')
            return redirect(url_for('admin.add_book'))

        rp_valid, rp_err = validate_price(request.form.get('rent_price'), "Rent price")
        if not rp_valid:
            flash(rp_err, 'danger')
            return redirect(url_for('admin.add_book'))

        qty = request.form.get('quantity', '0')
        if qty and qty != '0':
            q_valid, q_err = validate_quantity(qty)
            if not q_valid:
                flash(q_err, 'danger')
                return redirect(url_for('admin.add_book'))

        # Check for duplicate ISBN
        isbn = request.form.get('isbn', '').strip()
        if isbn:
            db = get_db()
            with db.cursor() as cur:
                cur.execute("SELECT id FROM books WHERE isbn = %s", (isbn,))
                if cur.fetchone():
                    flash('A book with this ISBN already exists.', 'danger')
                    return redirect(url_for('admin.add_book'))

        try:
            Book.create({
                'title': title,
                'isbn': isbn or None,
                'authors': request.form.get('authors', ''),
                'publisher': request.form.get('publisher'),
                'publication_date': request.form.get('publication_date') or None,
                'edition': request.form.get('edition'),
                'language': request.form.get('language', 'English'),
                'format': request.form.get('format', 'paperback'),
                'book_type': request.form.get('book_type', 'new'),
                'purchase_option': request.form.get('purchase_option', 'buy'),
                'buy_price': request.form.get('buy_price') or None,
                'rent_price': request.form.get('rent_price') or None,
                'quantity': request.form.get('quantity', 0),
                'category_id': request.form['category_id'],
                'keywords': request.form.get('keywords', '')
            })
            flash('Book added successfully!', 'success')
            return redirect(url_for('admin.manage_books'))
        except Exception:
            flash('Could not add book. Please check your inputs and try again.', 'danger')
            return redirect(url_for('admin.add_book'))
    categories = Book.get_categories()
    return render_template('admin/add_book.html', categories=categories)

@admin_bp.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@role_required('admin')
def edit_book(book_id):
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        t_valid, t_err = validate_name(title, "Title")
        if not t_valid:
            flash(t_err, 'danger')
            return redirect(url_for('admin.edit_book', book_id=book_id))

        bp_valid, bp_err = validate_price(request.form.get('buy_price'), "Buy price")
        if not bp_valid:
            flash(bp_err, 'danger')
            return redirect(url_for('admin.edit_book', book_id=book_id))

        rp_valid, rp_err = validate_price(request.form.get('rent_price'), "Rent price")
        if not rp_valid:
            flash(rp_err, 'danger')
            return redirect(url_for('admin.edit_book', book_id=book_id))

        # Prevent ISBN change during edit - use existing book's ISBN
        existing_book = Book.get_by_id(book_id)
        if not existing_book:
            flash('Book not found.', 'danger')
            return redirect(url_for('admin.manage_books'))

        try:
            Book.update(book_id, {
                'title': title,
                'isbn': existing_book['isbn'],
                'authors': request.form.get('authors', ''),
                'publisher': request.form.get('publisher'),
                'publication_date': request.form.get('publication_date') or None,
                'edition': request.form.get('edition'),
                'language': request.form.get('language', 'English'),
                'format': request.form.get('format', 'paperback'),
                'book_type': request.form.get('book_type', 'new'),
                'purchase_option': request.form.get('purchase_option', 'buy'),
                'buy_price': request.form.get('buy_price') or None,
                'rent_price': request.form.get('rent_price') or None,
                'quantity': request.form.get('quantity', 0),
                'category_id': request.form['category_id'],
                'keywords': request.form.get('keywords', '')
            })
            flash('Book updated!', 'success')
            return redirect(url_for('admin.manage_books'))
        except Exception:
            flash('Could not update book. Please try again.', 'danger')
            return redirect(url_for('admin.edit_book', book_id=book_id))
    book = Book.get_by_id(book_id)
    categories = Book.get_categories()
    return render_template('admin/edit_book.html', book=book, categories=categories)

@admin_bp.route('/books/delete/<int:book_id>', methods=['POST'])
@role_required('admin')
def delete_book(book_id):
    try:
        Book.delete(book_id)
        flash('Book deleted.', 'info')
    except Exception:
        flash('Could not delete book. It may be referenced by orders.', 'danger')
    return redirect(url_for('admin.manage_books'))

@admin_bp.route('/tickets')
@role_required('admin')
def tickets():
    my_tickets = TicketService.get_assigned_tickets(session['user_id'])
    return render_template('admin/tickets.html', tickets=my_tickets)

@admin_bp.route('/tickets/<int:ticket_id>')
@role_required('admin')
def ticket_detail(ticket_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT t.*, u.email as creator_email FROM tickets t 
                      JOIN users u ON t.creator_id = u.id 
                      WHERE t.id = %s AND t.assigned_admin_id = %s""", (ticket_id, session['user_id']))
        ticket = cur.fetchone()
    if not ticket:
        flash('Ticket not found or not assigned to you.', 'danger')
        return redirect(url_for('admin.tickets'))
    history = TicketService.get_ticket_history(ticket_id)
    return render_template('admin/ticket_detail.html', ticket=ticket, history=history)

@admin_bp.route('/tickets/<int:ticket_id>/update', methods=['POST'])
@role_required('admin')
def update_ticket(ticket_id):
    new_status = request.form.get('new_status')
    solution = request.form.get('solution')
    success, error = TicketService.update_ticket_status(ticket_id, new_status, session['user_id'], solution, session['user_id'])
    if success:
        flash(f'Ticket updated to {new_status}.', 'success')
    else:
        flash(error or 'Failed to update ticket.', 'danger')
    return redirect(url_for('admin.ticket_detail', ticket_id=ticket_id))

# ==================== PROFILE ====================

@admin_bp.route('/profile', methods=['GET', 'POST'])
@role_required('admin')
def profile():
    ep = EmployeeProfile.get_by_user_id(session['user_id'])
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        fn_valid, fn_err = validate_name(first_name, "First name")
        if not fn_valid:
            flash(fn_err, 'danger')
            return redirect(url_for('admin.profile'))
        ln_valid, ln_err = validate_name(last_name, "Last name")
        if not ln_valid:
            flash(ln_err, 'danger')
            return redirect(url_for('admin.profile'))
        phone = request.form.get('phone', '').strip()
        if phone:
            ph_valid, ph_err = validate_phone(phone)
            if not ph_valid:
                flash(ph_err, 'danger')
                return redirect(url_for('admin.profile'))
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""UPDATE employee_profiles SET first_name=%s, last_name=%s, gender=%s, phone=%s, address=%s
                          WHERE user_id=%s""",
                       (first_name, last_name, request.form.get('gender', 'other'),
                        phone or None, request.form.get('address', ''), session['user_id']))
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('admin.profile'))
    return render_template('admin/profile.html', profile=ep)

# ==================== UNIVERSITY MANAGEMENT ====================

@admin_bp.route('/universities')
@role_required('admin')
def universities():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM universities ORDER BY name")
        unis = cur.fetchall()
    return render_template('admin/universities.html', universities=unis)

@admin_bp.route('/universities/add', methods=['POST'])
@role_required('admin')
def add_university():
    name = request.form.get('name', '').strip()
    n_valid, n_err = validate_name(name, "University name")
    if not n_valid:
        flash(n_err, 'danger')
        return redirect(url_for('admin.universities'))
    rep_phone = request.form.get("rep_phone", "").strip()
    if rep_phone and (not rep_phone.isdigit() or len(rep_phone) != 10):
        flash("Rep phone number must be exactly 10 digits.", "danger")
        return redirect(url_for("admin.universities"))
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM universities WHERE LOWER(name) = LOWER(%s)", (name,))
            if cur.fetchone():
                flash('A university with this name already exists.', 'danger')
                return redirect(url_for('admin.universities'))
            cur.execute(
                "INSERT INTO universities (name, address, rep_first_name, rep_last_name, rep_email, rep_phone) VALUES (%s,%s,%s,%s,%s,%s)",
                (name, request.form.get('address'),
                 request.form.get('rep_first_name'), request.form.get('rep_last_name'),
                 request.form.get('rep_email'), request.form.get('rep_phone')))
        flash('University added!', 'success')
    except Exception:
        flash('Could not add university. It may already exist.', 'danger')
    return redirect(url_for('admin.universities'))

@admin_bp.route('/universities/delete/<int:uni_id>', methods=['POST'])
@role_required('admin')
def delete_university(uni_id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE student_profiles SET university_id = NULL, department_id = NULL WHERE university_id = %s", (uni_id,))
            cur.execute("DELETE FROM universities WHERE id = %s", (uni_id,))
        flash('University deleted.', 'info')
    except Exception:
        flash('Could not delete university. Please try again.', 'danger')
    return redirect(url_for('admin.universities'))

# ==================== DEPARTMENT MANAGEMENT ====================

@admin_bp.route('/departments')
@role_required('admin')
def departments():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT d.*, u.name as uni_name FROM departments d JOIN universities u ON d.university_id = u.id ORDER BY u.name, d.name")
        depts = cur.fetchall()
        cur.execute("SELECT * FROM universities ORDER BY name")
        unis = cur.fetchall()
    return render_template('admin/departments.html', departments=depts, universities=unis)

@admin_bp.route('/departments/add', methods=['POST'])
@role_required('admin')
def add_department():
    name = request.form.get('name', '').strip()
    n_valid, n_err = validate_name(name, "Department name")
    if not n_valid:
        flash(n_err, 'danger')
        return redirect(url_for('admin.departments'))
    db = get_db()
    with db.cursor() as cur:
        uni_id = request.form.get('university_id')
        if not uni_id:
            flash('Please select a university.', 'danger')
            return redirect(url_for('admin.departments'))
        try:
            cur.execute("INSERT INTO departments (name, university_id) VALUES (%s,%s)", (name, uni_id))
            flash('Department added!', 'success')
        except Exception:
            flash('Department already exists in this university.', 'danger')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/departments/delete/<int:dept_id>', methods=['POST'])
@role_required('admin')
def delete_department(dept_id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE student_profiles SET department_id = NULL WHERE department_id = %s", (dept_id,))
            cur.execute("DELETE FROM departments WHERE id = %s", (dept_id,))
        flash('Department deleted.', 'info')
    except Exception:
        flash('Could not delete department.', 'danger')
    return redirect(url_for('admin.departments'))

# ==================== INSTRUCTOR MANAGEMENT ====================

@admin_bp.route('/instructors')
@role_required('admin')
def instructors():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT i.*, CONCAT(i.first_name, ' ', i.last_name) as full_name,
                      u.name as uni_name, d.name as dept_name
                      FROM instructors i
                      JOIN universities u ON i.university_id = u.id
                      JOIN departments d ON i.department_id = d.id
                      ORDER BY i.first_name""")
        instr = cur.fetchall()
        cur.execute("SELECT * FROM universities ORDER BY name")
        unis = cur.fetchall()
        cur.execute("SELECT d.*, u.name as uni_name FROM departments d JOIN universities u ON d.university_id = u.id ORDER BY u.name, d.name")
        depts = cur.fetchall()
    return render_template('admin/instructors.html', instructors=instr, universities=unis, departments=depts)

@admin_bp.route('/instructors/add', methods=['POST'])
@role_required('admin')
def add_instructor():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    fn_valid, fn_err = validate_name(first_name, "First name")
    if not fn_valid:
        flash(fn_err, 'danger')
        return redirect(url_for('admin.instructors'))
    ln_valid, ln_err = validate_name(last_name, "Last name")
    if not ln_valid:
        flash(ln_err, 'danger')
        return redirect(url_for('admin.instructors'))
    email = request.form.get('email', '').strip()
    em_valid, em_err = validate_email(email, "Instructor email")
    if not em_valid:
        flash(em_err, 'danger')
        return redirect(url_for('admin.instructors'))
    db = get_db()
    try:
        with db.cursor() as cur:
            # Check for duplicate email
            cur.execute("SELECT id FROM instructors WHERE LOWER(email) = LOWER(%s)", (email,))
            if cur.fetchone():
                flash('An instructor with this email already exists.', 'danger')
                return redirect(url_for('admin.instructors'))
            cur.execute("INSERT INTO instructors (first_name, last_name, email, university_id, department_id) VALUES (%s,%s,%s,%s,%s)",
                       (first_name, last_name, email,
                        request.form['university_id'], request.form['department_id']))
        flash('Instructor added!', 'success')
    except Exception as e:
        if '45000' in str(e):
            flash('Instructor department must belong to the selected university.', 'danger')
        else:
            flash('Could not add instructor.', 'danger')
    return redirect(url_for('admin.instructors'))

@admin_bp.route('/instructors/delete/<int:instr_id>', methods=['POST'])
@role_required('admin')
def delete_instructor(instr_id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM instructors WHERE id = %s", (instr_id,))
        flash('Instructor deleted.', 'info')
    except Exception:
        flash('Could not delete instructor.', 'danger')
    return redirect(url_for('admin.instructors'))

# ==================== COURSE MANAGEMENT ====================

@admin_bp.route('/courses')
@role_required('admin')
def courses():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT c.*, u.name as uni_name FROM courses c
                      JOIN universities u ON c.university_id = u.id ORDER BY c.name""")
        courses_list = cur.fetchall()
        # Fetch departments and instructors for each course
        for course in courses_list:
            cur.execute("""SELECT d.name FROM course_departments cd
                          JOIN departments d ON cd.department_id = d.id
                          WHERE cd.course_id = %s""", (course['id'],))
            course['departments'] = [r['name'] for r in cur.fetchall()]
            cur.execute("""SELECT CONCAT(i.first_name, ' ', i.last_name) as name
                          FROM course_instructors ci
                          JOIN instructors i ON ci.instructor_id = i.id
                          WHERE ci.course_id = %s""", (course['id'],))
            course['instructors'] = [r['name'] for r in cur.fetchall()]
        cur.execute("SELECT * FROM universities ORDER BY name")
        unis = cur.fetchall()
        cur.execute("SELECT d.*, u.name as uni_name FROM departments d JOIN universities u ON d.university_id = u.id ORDER BY u.name, d.name")
        depts = cur.fetchall()
        cur.execute("SELECT i.*, u.name as uni_name FROM instructors i JOIN universities u ON i.university_id = u.id ORDER BY i.first_name")
        instrs = cur.fetchall()
    return render_template('admin/courses.html', courses=courses_list, universities=unis, departments=depts, instructors=instrs)

@admin_bp.route('/courses/add', methods=['POST'])
@role_required('admin')
def add_course():
    name = request.form.get('name', '').strip()
    n_valid, n_err = validate_name(name, "Course name")
    if not n_valid:
        flash(n_err, 'danger')
        return redirect(url_for('admin.courses'))
    uni_id = request.form['university_id']
    db = get_db()
    try:
        with db.cursor() as cur:
            # Check for duplicate course name within same university
            cur.execute("SELECT id FROM courses WHERE LOWER(name) = LOWER(%s) AND university_id = %s", (name, uni_id))
            if cur.fetchone():
                flash('A course with this name already exists in the selected university.', 'danger')
                return redirect(url_for('admin.courses'))
            cur.execute("INSERT INTO courses (name, code, university_id, year, semester) VALUES (%s,%s,%s,%s,%s)",
                       (name, request.form.get('code'), uni_id,
                        request.form.get('year') or None, request.form.get('semester') or None))
            course_id = cur.lastrowid
            dept_ids = request.form.getlist('department_ids')
            for did in dept_ids:
                cur.execute("INSERT INTO course_departments (course_id, department_id) VALUES (%s,%s)", (course_id, did))
            instr_ids = request.form.getlist('instructor_ids')
            for iid in instr_ids:
                cur.execute("INSERT INTO course_instructors (course_id, instructor_id) VALUES (%s,%s)", (course_id, iid))
        flash('Course added!', 'success')
    except Exception:
        flash('Could not add course. It may already exist.', 'danger')
    return redirect(url_for('admin.courses'))

@admin_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
@role_required('admin')
def delete_course(course_id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM courses WHERE id = %s", (course_id,))
        flash('Course deleted.', 'info')
    except Exception:
        flash('Could not delete course.', 'danger')
    return redirect(url_for('admin.courses'))

# ==================== COURSE-BOOK MANAGEMENT ====================

@admin_bp.route('/course-books')
@role_required('admin')
def course_books():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT cb.*, c.name as course_name, b.title as book_title,
                      u.name as uni_name,
                      CONCAT(i.first_name, ' ', i.last_name) as instructor_name
                      FROM course_books cb
                      JOIN courses c ON cb.course_id = c.id
                      JOIN universities u ON c.university_id = u.id
                      JOIN books b ON cb.book_id = b.id
                      LEFT JOIN instructors i ON cb.instructor_id = i.id
                      ORDER BY c.name, b.title""")
        links = cur.fetchall()
        cur.execute("SELECT * FROM courses ORDER BY name")
        courses_list = cur.fetchall()
        cur.execute("SELECT * FROM books ORDER BY title")
        books = cur.fetchall()
        cur.execute("SELECT i.*, CONCAT(i.first_name, ' ', i.last_name) as full_name FROM instructors i ORDER BY i.first_name")
        instrs = cur.fetchall()
        cur.execute("SELECT * FROM universities ORDER BY name")
        unis = cur.fetchall()
    return render_template('admin/course_books.html', links=links, courses=courses_list, books=books, instructors=instrs, universities=unis)

@admin_bp.route('/course-books/add', methods=['POST'])
@role_required('admin')
def add_course_book():
    db = get_db()
    try:
        with db.cursor() as cur:
            # Check for duplicate
            cur.execute(
                "SELECT id FROM course_books WHERE course_id = %s AND book_id = %s",
                (request.form['course_id'], request.form['book_id'])
            )
            if cur.fetchone():
                flash('This book is already linked to the selected course.', 'warning')
                return redirect(url_for('admin.course_books'))

            cur.execute("INSERT INTO course_books (course_id, book_id, link_type, year, semester, instructor_id) VALUES (%s,%s,%s,%s,%s,%s)",
                       (request.form['course_id'], request.form['book_id'],
                        request.form.get('link_type', 'recommended'),
                        request.form.get('year') or None, request.form.get('semester') or None,
                        request.form.get('instructor_id') or None))
        flash('Course-book link added!', 'success')
    except Exception:
        flash('Could not add link.', 'danger')
    return redirect(url_for('admin.course_books'))


@admin_bp.route('/course-books/delete/<int:link_id>', methods=['POST'])
@role_required('admin')
def delete_course_book(link_id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM course_books WHERE id = %s", (link_id,))
        flash('Link removed.', 'info')
    except Exception:
        flash('Could not remove link.', 'danger')
    return redirect(url_for('admin.course_books'))

@admin_bp.route('/course-books/<int:link_id>')
@role_required('admin')
def course_book_detail(link_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT cb.*, c.name as course_name, b.title as book_title,
                      CONCAT(i.first_name, ' ', i.last_name) as instructor_name
                      FROM course_books cb
                      JOIN courses c ON cb.course_id = c.id
                      JOIN books b ON cb.book_id = b.id
                      LEFT JOIN instructors i ON cb.instructor_id = i.id
                      WHERE cb.id = %s""", (link_id,))
        link = cur.fetchone()
    if not link:
        flash('Link not found.', 'danger')
        return redirect(url_for('admin.course_books'))
    return render_template('admin/course_book.html', link=link)

# ==================== API ENDPOINTS ====================

@admin_bp.route('/api/departments/<int:uni_id>')
@role_required('admin')
def api_departments(uni_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, name FROM departments WHERE university_id = %s ORDER BY name", (uni_id,))
        depts = cur.fetchall()
    return jsonify(depts)

@admin_bp.route('/api/instructors/<int:uni_id>')
@role_required('admin')
def api_instructors(uni_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT i.id, CONCAT(i.first_name, ' ', i.last_name) as full_name
                      FROM instructors i WHERE i.university_id = %s ORDER BY i.first_name""", (uni_id,))
        instrs = cur.fetchall()
    return jsonify(instrs)

@admin_bp.route('/api/courses/<int:uni_id>')
@role_required('admin')
def api_courses(uni_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, name, code, year, semester FROM courses WHERE university_id = %s ORDER BY name", (uni_id,))
        courses_list = cur.fetchall()
    return jsonify(courses_list)

@admin_bp.route('/api/course-instructors/<int:course_id>')
@role_required('admin')
def api_course_instructors(course_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT i.id, CONCAT(i.first_name, ' ', i.last_name) as full_name
                      FROM course_instructors ci
                      JOIN instructors i ON ci.instructor_id = i.id
                      WHERE ci.course_id = %s ORDER BY i.first_name""", (course_id,))
        instrs = cur.fetchall()
    return jsonify(instrs)
