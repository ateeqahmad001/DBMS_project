from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.decorators import role_required
from services.ticket_service import TicketService
from services.order_service import OrderService
from models.user import User

support_bp = Blueprint('support', __name__, url_prefix='/support')

@support_bp.route('/dashboard')
@role_required('support')
def dashboard():
    tickets = TicketService.get_all_tickets()
    cancel_requests = OrderService.get_cancellation_requests()
    new_tickets = [t for t in tickets if t['status'] == 'new']
    return render_template('support/dashboard.html', tickets=tickets, cancel_requests=cancel_requests, new_tickets=new_tickets)

@support_bp.route('/tickets')
@role_required('support')
def tickets():
    all_tickets = TicketService.get_all_tickets()
    admins = User.get_all_by_role('admin')
    return render_template('support/tickets.html', tickets=all_tickets, admins=admins)

@support_bp.route('/tickets/create', methods=['GET', 'POST'])
@role_required('support')
def create_ticket():
    admins = User.get_all_by_role('admin')
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'other')
        assign_admin_id = request.form.get('assign_admin_id')

        if not title or not description:
            flash('Title and description are required.', 'danger')
            return render_template('support/create_ticket.html', admins=admins)

        try:
            ticket_id = TicketService.create_ticket(session['user_id'], title, description, category)
            # If admin selected, assign immediately
            if assign_admin_id:
                success, error = TicketService.assign_ticket(ticket_id, int(assign_admin_id), session['user_id'])
                if success:
                    flash('Ticket created and assigned successfully.', 'success')
                else:
                    flash(f'Ticket created but assignment failed: {error}', 'warning')
            else:
                flash('Ticket created successfully.', 'success')
            return redirect(url_for('support.tickets'))
        except Exception:
            flash('Could not create ticket. Please try again.', 'danger')
            return render_template('support/create_ticket.html', admins=admins)

    return render_template('support/create_ticket.html', admins=admins)

@support_bp.route('/tickets/<int:ticket_id>/assign', methods=['POST'])
@role_required('support')
def assign_ticket(ticket_id):
    admin_id = request.form.get('admin_id')
    if not admin_id:
        flash('Please select an admin.', 'danger')
        return redirect(url_for('support.tickets'))
    success, error = TicketService.assign_ticket(ticket_id, int(admin_id), session['user_id'])
    if success:
        flash('Ticket assigned successfully.', 'success')
    else:
        flash(error or 'Failed to assign ticket.', 'danger')
    return redirect(url_for('support.tickets'))

@support_bp.route('/tickets/<int:ticket_id>')
@role_required('support')
def ticket_detail(ticket_id):
    from database.db import get_db
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT t.*, u.email as creator_email FROM tickets t JOIN users u ON t.creator_id = u.id WHERE t.id = %s", (ticket_id,))
        ticket = cur.fetchone()
    if not ticket:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('support.tickets'))
    history = TicketService.get_ticket_history(ticket_id)
    admins = User.get_all_by_role('admin')
    return render_template('support/ticket_detail.html', ticket=ticket, history=history, admins=admins)

@support_bp.route('/cancellations')
@role_required('support')
def cancellations():
    requests = OrderService.get_cancellation_requests()
    return render_template('support/cancellations.html', requests=requests)

@support_bp.route('/cancellations/<int:order_id>/approve', methods=['POST'])
@role_required('support')
def approve_cancel(order_id):
    if OrderService.approve_cancellation(order_id, session['user_id']):
        flash('Cancellation approved.', 'success')
    else:
        flash('Failed to approve cancellation.', 'danger')
    return redirect(url_for('support.cancellations'))

@support_bp.route('/cancellations/<int:order_id>/reject', methods=['POST'])
@role_required('support')
def reject_cancel(order_id):
    if OrderService.reject_cancellation(order_id, session['user_id']):
        flash('Cancellation rejected.', 'info')
    else:
        flash('Failed to reject cancellation.', 'danger')
    return redirect(url_for('support.cancellations'))

# ==================== PROFILE ====================

@support_bp.route('/profile', methods=['GET', 'POST'])
@role_required('support')
def profile():
    from models.employee import EmployeeProfile
    from utils.validators import validate_name, validate_phone
    ep = EmployeeProfile.get_by_user_id(session['user_id'])
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        fn_valid, fn_err = validate_name(first_name, "First name")
        if not fn_valid:
            flash(fn_err, 'danger')
            return redirect(url_for('support.profile'))
        ln_valid, ln_err = validate_name(last_name, "Last name")
        if not ln_valid:
            flash(ln_err, 'danger')
            return redirect(url_for('support.profile'))
        phone = request.form.get('phone', '').strip()
        if phone:
            ph_valid, ph_err = validate_phone(phone)
            if not ph_valid:
                flash(ph_err, 'danger')
                return redirect(url_for('support.profile'))
        from database.db import get_db
        db = get_db()
        with db.cursor() as cur:
            cur.execute("""UPDATE employee_profiles SET first_name=%s, last_name=%s, gender=%s, phone=%s, address=%s
                          WHERE user_id=%s""",
                       (first_name, last_name, request.form.get('gender', 'other'),
                        phone or None, request.form.get('address', ''), session['user_id']))
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('support.profile'))
    return render_template('support/profile.html', profile=ep)
