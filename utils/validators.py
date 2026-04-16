import re

def validate_phone(phone):
    """Phone must be exactly 10 digits."""
    if not phone:
        return True, None  # optional
    phone = phone.strip()
    if not re.match(r'^\d{10}$', phone):
        return False, "Phone number must be exactly 10 digits."
    return True, None

def validate_aadhaar(aadhaar):
    """Aadhaar must be exactly 12 digits."""
    if not aadhaar:
        return True, None
    aadhaar = aadhaar.strip()
    if not re.match(r'^\d{12}$', aadhaar):
        return False, "Aadhaar number must be exactly 12 digits."
    return True, None

def validate_name(name, field_label="Name"):
    """Name cannot be numeric-only."""
    if not name:
        return False, f"{field_label} is required."
    name = name.strip()
    if not name:
        return False, f"{field_label} is required."
    if re.match(r'^\d+$', name):
        return False, f"{field_label} cannot be numeric-only."
    return True, None

def validate_price(price_str, field_label="Price"):
    """Price must be >= 0."""
    if price_str is None or price_str == '':
        return True, None
    try:
        price = float(price_str)
        if price < 0:
            return False, f"{field_label} must be >= 0."
        return True, None
    except (ValueError, TypeError):
        return False, f"{field_label} must be a valid number."

def validate_quantity(qty_str, field_label="Quantity"):
    """Quantity must be >= 1."""
    if qty_str is None or qty_str == '':
        return True, None
    try:
        qty = int(qty_str)
        if qty < 1:
            return False, f"{field_label} must be >= 1."
        return True, None
    except (ValueError, TypeError):
        return False, f"{field_label} must be a valid integer."

def validate_card_number(card_number):
    """Card number must be 13-19 digits."""
    if not card_number:
        return False, "Card number is required."
    card_number = re.sub(r'[\s\-]', '', card_number.strip())
    if not re.match(r'^\d{13,19}$', card_number):
        return False, "Card number must be 13-19 digits."
    return True, None

def validate_salary(salary_str):
    """Salary must be >= 0."""
    if salary_str is None or salary_str == '':
        return True, None
    try:
        salary = float(salary_str)
        if salary < 0:
            return False, "Salary must be >= 0."
        return True, None
    except (ValueError, TypeError):
        return False, "Salary must be a valid number."


def validate_email(email, field_label="Email"):
    """Email must be a valid format."""
    if not email:
        return False, f"{field_label} is required."
    email = email.strip()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False, f"{field_label} must be a valid email address."
    return True, None
