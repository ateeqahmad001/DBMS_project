from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.validators import validate_name, validate_phone
from models.user import User
from models.student import StudentProfile
from database.db import get_db
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        role = session['role']
        if role == 'superadmin':
            return redirect(url_for('super_admin.dashboard'))
        return redirect(url_for(f"{role}.dashboard"))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.find_by_email(email)
        if not user:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')
        
        if not user.get('is_active', True):
            flash('Account is inactive. Contact Super Admin.', 'danger')
            return render_template('auth/login.html')

        if not User.verify_password(password, user['password_hash']):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        session['user_id'] = user['id']
        session['email'] = user['email']
        session['role'] = user['role']

        flash('Welcome back!', 'success')

        if user['role'] == 'superadmin':
            return redirect(url_for('super_admin.dashboard'))
        elif user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user['role'] == 'support':
            return redirect(url_for('support.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/api/departments/<int:uni_id>')
def api_departments(uni_id):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id, name FROM departments WHERE university_id = %s ORDER BY name", (uni_id,))
        depts = cur.fetchall()
    return jsonify(depts)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    db = get_db()
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        with db.cursor() as cur:
            cur.execute("SELECT * FROM universities ORDER BY name")
            unis = cur.fetchall()

        if not all([email, password, first_name, last_name]):
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/register.html', universities=unis)

        fn_valid, fn_err = validate_name(first_name, "First name")
        if not fn_valid:
            flash(fn_err, 'danger')
            return render_template('auth/register.html', universities=unis)
        ln_valid, ln_err = validate_name(last_name, "Last name")
        if not ln_valid:
            flash(ln_err, 'danger')
            return render_template('auth/register.html', universities=unis)

        phone = request.form.get('phone', '').strip()
        ph_valid, ph_err = validate_phone(phone)
        if not ph_valid:
            flash(ph_err, 'danger')
            return render_template('auth/register.html', universities=unis)

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', universities=unis)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html', universities=unis)

        existing = User.find_by_email(email)
        if existing:
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', universities=unis)

        try:
            user_id = User.create_user(email, password, 'student')
            StudentProfile.create(user_id, {
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

            from services.cart_service import CartService
            CartService.get_or_create_cart(user_id)

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            flash('Registration failed. Please try again.', 'danger')
            return render_template('auth/register.html', universities=unis)

    with db.cursor() as cur:
        cur.execute("SELECT * FROM universities ORDER BY name")
        unis = cur.fetchall()
    return render_template('auth/register.html', universities=unis)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
