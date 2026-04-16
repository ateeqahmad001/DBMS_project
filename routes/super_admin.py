from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.decorators import role_required
from utils.validators import validate_name, validate_phone, validate_aadhaar, validate_salary
from models.user import User
from models.employee import EmployeeProfile
from database.db import get_db

super_admin_bp = Blueprint('super_admin', __name__, url_prefix='/super-admin')

@super_admin_bp.route('/dashboard')
@role_required('superadmin')
def dashboard():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'admin'")
        admin_count = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'support'")
        support_count = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'student'")
        student_count = cur.fetchone()['cnt']
    return render_template('super_admin/dashboard.html',
        admin_count=admin_count, support_count=support_count,
        student_count=student_count)

@super_admin_bp.route('/universities')
@role_required('superadmin')
def universities():
    db = get_db()
    uni_id = request.args.get('uni_id', type=int)
    with db.cursor() as cur:
        cur.execute("SELECT id, name FROM universities ORDER BY name")
        all_universities = cur.fetchall()

        selected_uni = None
        students = []
        if uni_id:
            cur.execute("SELECT id, name FROM universities WHERE id = %s", (uni_id,))
            selected_uni = cur.fetchone()
            if selected_uni:
                cur.execute("""
                    SELECT sp.first_name, sp.last_name, u.email, sp.major as course,
                           COALESCE(d.name, '') as department_name
                    FROM student_profiles sp
                    JOIN users u ON sp.user_id = u.id
                    LEFT JOIN departments d ON sp.department_id = d.id
                    WHERE sp.university_id = %s
                    ORDER BY sp.first_name
                """, (uni_id,))
                students = cur.fetchall()

    return render_template('super_admin/universities.html',
        universities=all_universities, selected_uni=selected_uni, students=students)

@super_admin_bp.route('/employees')
@role_required('superadmin')
def employees():
    db = get_db()
    role_filter = request.args.get('role', 'all')
    with db.cursor() as cur:
        if role_filter == 'admin':
            cur.execute("""SELECT ep.*, u.email, u.role, u.is_active FROM employee_profiles ep
                JOIN users u ON ep.user_id = u.id WHERE u.role = 'admin' ORDER BY ep.first_name""")
        elif role_filter == 'support':
            cur.execute("""SELECT ep.*, u.email, u.role, u.is_active FROM employee_profiles ep
                JOIN users u ON ep.user_id = u.id WHERE u.role = 'support' ORDER BY ep.first_name""")
        else:
            cur.execute("""SELECT ep.*, u.email, u.role, u.is_active FROM employee_profiles ep
                JOIN users u ON ep.user_id = u.id WHERE u.role IN ('admin','support') ORDER BY ep.first_name""")
        employees = cur.fetchall()
    return render_template('super_admin/employees.html', employees=employees, role_filter=role_filter)

@super_admin_bp.route('/add-employee', methods=['GET', 'POST'])
@role_required('superadmin')
def add_employee():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', '')

        if role not in ('admin', 'support'):
            flash('Invalid role.', 'danger')
            return render_template('super_admin/add_employee.html')

        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        fn_valid, fn_err = validate_name(first_name, "First name")
        if not fn_valid:
            flash(fn_err, 'danger')
            return render_template('super_admin/add_employee.html')
        ln_valid, ln_err = validate_name(last_name, "Last name")
        if not ln_valid:
            flash(ln_err, 'danger')
            return render_template('super_admin/add_employee.html')

        phone = request.form.get('phone', '').strip()
        ph_valid, ph_err = validate_phone(phone)
        if not ph_valid:
            flash(ph_err, 'danger')
            return render_template('super_admin/add_employee.html')

        aadhaar = request.form.get('aadhaar', '').strip()
        aa_valid, aa_err = validate_aadhaar(aadhaar)
        if not aa_valid:
            flash(aa_err, 'danger')
            return render_template('super_admin/add_employee.html')

        salary = request.form.get('salary', '').strip()
        s_valid, s_err = validate_salary(salary)
        if not s_valid:
            flash(s_err, 'danger')
            return render_template('super_admin/add_employee.html')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('super_admin/add_employee.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('super_admin/add_employee.html')

        existing = User.find_by_email(email)
        if existing:
            flash('Email already exists.', 'danger')
            return render_template('super_admin/add_employee.html')

        employee_id = request.form.get('employee_id', '').strip()
        if not employee_id:
            flash('Employee ID is required.', 'danger')
            return render_template('super_admin/add_employee.html')

        db = get_db()
        try:
            db.autocommit(False)
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
                    (email, User._hash_password(password), role)
                )
                user_id = cur.lastrowid
                cur.execute(
                    """INSERT INTO employee_profiles (user_id, employee_id, first_name, last_name, gender, salary, aadhaar, phone, address)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (user_id, employee_id, first_name, last_name,
                     request.form.get('gender', 'other'), salary or None, aadhaar or None,
                     phone or None, request.form.get('address', ''))
                )
            db.commit()
            flash(f'{role.capitalize()} employee added successfully!', 'success')
            return redirect(url_for('super_admin.employees'))
        except Exception as e:
            db.rollback()
            err_str = str(e)
            if 'Duplicate' in err_str or 'uq_emp' in err_str:
                if 'aadhaar' in err_str.lower():
                    flash('An employee with this Aadhaar number already exists.', 'danger')
                elif 'employee_id' in err_str.lower() or 'uq_emp_id' in err_str.lower():
                    flash('An employee with this Employee ID already exists.', 'danger')
                elif 'email' in err_str.lower():
                    flash('This email is already registered.', 'danger')
                else:
                    flash('A duplicate record was found. Please check your inputs.', 'danger')
            else:
                flash('Could not create employee. Please try again.', 'danger')
            return render_template('super_admin/add_employee.html')
        finally:
            db.autocommit(True)

    return render_template('super_admin/add_employee.html')

@super_admin_bp.route('/toggle-status/<int:user_id>', methods=['POST'])
@role_required('superadmin')
def toggle_employee_status(user_id):
    action = request.form.get('action')
    db = get_db()
    with db.cursor() as cur:
        if action == 'deactivate':
            cur.execute("UPDATE users SET is_active = FALSE WHERE id = %s AND role IN ('admin','support')", (user_id,))
            db.commit()
            flash('Account deactivated.', 'success')
        elif action == 'activate':
            cur.execute("UPDATE users SET is_active = TRUE WHERE id = %s AND role IN ('admin','support')", (user_id,))
            db.commit()
            flash('Account activated.', 'success')
        else:
            flash('Invalid action.', 'danger')
    return redirect(url_for('super_admin.employees'))

@super_admin_bp.route('/universities/<int:uni_id>/students')
@role_required('superadmin')
def university_students(uni_id):
    return redirect(url_for('super_admin.universities', uni_id=uni_id))

