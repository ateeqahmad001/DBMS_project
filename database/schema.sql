DROP DATABASE IF EXISTS gyanpustak;
CREATE DATABASE gyanpustak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gyanpustak;

-- ============================================================
-- 1. USERS TABLE
-- ============================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('superadmin','admin','support','student') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_email (email)
);

-- Index on email for fast lookups
CREATE INDEX idx_users_email ON users(email);

-- ============================================================
-- 2. EMPLOYEE PROFILES
-- ============================================================
CREATE TABLE employee_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    employee_id VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender ENUM('male','female','other'),
    salary DECIMAL(10,2) CHECK (salary >= 0),
    aadhaar VARCHAR(12),
    phone VARCHAR(20),
    address TEXT,
    UNIQUE KEY uq_emp_user (user_id),
    UNIQUE KEY uq_emp_id (employee_id),
    UNIQUE KEY uq_emp_aadhaar (aadhaar),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- 3. UNIVERSITIES
-- ============================================================
CREATE TABLE universities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    address TEXT,
    rep_first_name VARCHAR(100),
    rep_last_name VARCHAR(100),
    rep_email VARCHAR(255),
    rep_phone VARCHAR(20)
);

-- ============================================================
-- 4. DEPARTMENTS (belong to exactly one university)
-- ============================================================
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    university_id INT NOT NULL,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE KEY uq_dept_uni (name, university_id)
);

-- ============================================================
-- 5. STUDENT PROFILES
-- ============================================================
CREATE TABLE student_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    dob DATE,
    address TEXT,
    university_id INT,
    department_id INT,
    major VARCHAR(255),
    student_status ENUM('UG','PG') DEFAULT 'UG',
    year INT,
    UNIQUE KEY uq_sp_user (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

-- ============================================================
-- 6. INSTRUCTORS (belong to exactly one university + department)
-- ============================================================
CREATE TABLE instructors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    university_id INT NOT NULL,
    department_id INT NOT NULL,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- ============================================================
-- 7. COURSES (belong to exactly one university)
-- ============================================================
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    university_id INT NOT NULL,
    year INT,
    semester VARCHAR(50),
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE KEY uq_course_name_uni (name, university_id)
);

-- ============================================================
-- 8. COURSE-DEPARTMENT LINKING
-- ============================================================
CREATE TABLE course_departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    department_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
    UNIQUE KEY uq_cd (course_id, department_id)
);

-- ============================================================
-- 9. COURSE-INSTRUCTOR LINKING
-- ============================================================
CREATE TABLE course_instructors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    instructor_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE CASCADE,
    UNIQUE KEY uq_ci (course_id, instructor_id)
);

-- ============================================================
-- 10. CATEGORIES
-- ============================================================
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- ============================================================
-- 11. AUTHORS (normalized - M:N with books)
-- ============================================================
CREATE TABLE authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    UNIQUE KEY uq_author_name (name)
);

-- ============================================================
-- 12. KEYWORDS (normalized - M:N with books)
-- ============================================================
CREATE TABLE keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    UNIQUE KEY uq_keyword_name (name)
);

CREATE INDEX idx_keywords_name ON keywords(name);

-- ============================================================
-- 13. BOOKS (normalized: no authors, keywords, avg_rating columns)
-- ============================================================
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    isbn VARCHAR(20),
    publisher VARCHAR(255),
    publication_date DATE,
    edition VARCHAR(50),
    language VARCHAR(50) DEFAULT 'English',
    format ENUM('hardcover','paperback','ebook') DEFAULT 'paperback',
    book_type ENUM('new','used') DEFAULT 'new',
    purchase_option ENUM('buy','rent','both') DEFAULT 'buy',
    buy_price DECIMAL(10,2) CHECK (buy_price >= 0),
    rent_price DECIMAL(10,2) CHECK (rent_price >= 0),
    quantity INT DEFAULT 0 CHECK (quantity >= 0),
    category_id INT NOT NULL,
    image_url VARCHAR(500) DEFAULT '/static/images/book_placeholder.png',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_books_isbn (isbn),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_isbn ON books(isbn);

-- ============================================================
-- 14. BOOK-AUTHORS (M:N)
-- ============================================================
CREATE TABLE book_authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
    UNIQUE KEY uq_ba (book_id, author_id)
);

-- ============================================================
-- 15. BOOK-KEYWORDS (M:N)
-- ============================================================
CREATE TABLE book_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    keyword_id INT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES keywords(id) ON DELETE CASCADE,
    UNIQUE KEY uq_bk (book_id, keyword_id)
);

-- ============================================================
-- 16. BOOK SUBCATEGORIES
-- ============================================================
CREATE TABLE book_subcategories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- ============================================================
-- 17. COURSE-BOOK LINKING
-- ============================================================
CREATE TABLE course_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    book_id INT NOT NULL,
    link_type ENUM('required','recommended') DEFAULT 'recommended',
    year INT,
    semester VARCHAR(50),
    instructor_id INT,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE SET NULL
);

-- ============================================================
-- 18. CARTS (one per student - enforced by UNIQUE)
-- ============================================================
CREATE TABLE carts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_cart_student (student_id),
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- 19. CART ITEMS
-- ============================================================
CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1 CHECK (quantity > 0),
    is_rental BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE KEY uq_ci_book_type (cart_id, book_id, is_rental)
);

-- ============================================================
-- 20. ORDERS (updated: credit card fields, new shipping types)
-- ============================================================
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipping_type ENUM('standard','2-day','1-day') DEFAULT 'standard',
    shipping_address TEXT,
    credit_card_number VARCHAR(20),
    expiry_date VARCHAR(7),
    card_holder_name VARCHAR(255),
    card_type ENUM('visa','mastercard','amex','discover','rupay') DEFAULT NULL,
    payment_status ENUM('pending','paid','failed') DEFAULT 'pending',
    total_amount DECIMAL(10,2) DEFAULT 0.00 CHECK (total_amount >= 0),
    order_status ENUM('new','processed','awaiting_shipping','shipped','completed','cancel_requested','cancelled') DEFAULT 'new',
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_orders_student ON orders(student_id);

-- ============================================================
-- 21. ORDER ITEMS
-- ============================================================
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1 CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    is_rental BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- ============================================================
-- 22. ORDER CANCELLATIONS (separate table for approval flow)
-- ============================================================
CREATE TABLE order_cancellations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    reason TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    original_status ENUM('new','processed','awaiting_shipping','shipped') NOT NULL,
    approved_by INT DEFAULT NULL,
    decision ENUM('pending','approved','rejected') DEFAULT 'pending',
    decided_at TIMESTAMP NULL,
    UNIQUE KEY uq_oc_order (order_id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================
-- 23. REVIEWS (only for completed orders)
-- ============================================================
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    student_id INT NOT NULL,
    order_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    UNIQUE KEY uq_review (book_id, student_id, order_id)
);

-- ============================================================
-- 24. TICKETS
-- ============================================================
CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    problem TEXT NOT NULL,
    solution TEXT,
    category ENUM('user_profile','products','cart','orders','other') DEFAULT 'other',
    status ENUM('new','assigned','in-process','completed') DEFAULT 'new',
    assigned_admin_id INT,
    date_logged TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_admin_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_tickets_status ON tickets(status);

-- ============================================================
-- 25. TICKET HISTORY
-- ============================================================
CREATE TABLE ticket_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    changed_by INT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Trigger: Enforce exactly ONE superadmin
DELIMITER //
CREATE TRIGGER trg_enforce_single_superadmin_insert
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.role = 'superadmin' THEN
        IF (SELECT COUNT(*) FROM users WHERE role = 'superadmin') >= 1 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only one superadmin is allowed.';
        END IF;
    END IF;
END//

CREATE TRIGGER trg_enforce_single_superadmin_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    IF NEW.role = 'superadmin' AND OLD.role != 'superadmin' THEN
        IF (SELECT COUNT(*) FROM users WHERE role = 'superadmin') >= 1 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only one superadmin is allowed.';
        END IF;
    END IF;
END//

-- Trigger: Prevent multiple carts per student
CREATE TRIGGER trg_single_cart_per_student
BEFORE INSERT ON carts
FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*) FROM carts WHERE student_id = NEW.student_id) >= 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Student already has a cart.';
    END IF;
END//

-- Trigger: Auto-log ticket status changes
CREATE TRIGGER trg_ticket_status_change
AFTER UPDATE ON tickets
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO ticket_history (ticket_id, old_status, new_status, changed_by, notes)
        VALUES (NEW.id, OLD.status, NEW.status, COALESCE(NEW.assigned_admin_id, NEW.creator_id), CONCAT('Status changed from ', OLD.status, ' to ', NEW.status));
    END IF;
END//

-- Trigger: Ensure review only for completed orders
CREATE TRIGGER trg_review_completed_order
BEFORE INSERT ON reviews
FOR EACH ROW
BEGIN
    DECLARE os VARCHAR(50);
    SELECT order_status INTO os FROM orders WHERE id = NEW.order_id;
    IF os != 'completed' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reviews are only allowed for completed orders.';
    END IF;
END//

-- Trigger: Validate course-instructor university consistency
CREATE TRIGGER trg_course_instructor_uni_check
BEFORE INSERT ON course_instructors
FOR EACH ROW
BEGIN
    DECLARE c_uni INT;
    DECLARE i_uni INT;
    SELECT university_id INTO c_uni FROM courses WHERE id = NEW.course_id;
    SELECT university_id INTO i_uni FROM instructors WHERE id = NEW.instructor_id;
    IF c_uni != i_uni THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Instructor must belong to the same university as the course.';
    END IF;
END//

-- Trigger: Validate course-department university consistency
CREATE TRIGGER trg_course_dept_uni_check
BEFORE INSERT ON course_departments
FOR EACH ROW
BEGIN
    DECLARE c_uni INT;
    DECLARE d_uni INT;
    SELECT university_id INTO c_uni FROM courses WHERE id = NEW.course_id;
    SELECT university_id INTO d_uni FROM departments WHERE id = NEW.department_id;
    IF c_uni != d_uni THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Department must belong to the same university as the course.';
    END IF;
END//

-- Trigger: Validate instructor department belongs to instructor's university
CREATE TRIGGER trg_instructor_dept_uni_check
BEFORE INSERT ON instructors
FOR EACH ROW
BEGIN
    DECLARE d_uni INT;
    SELECT university_id INTO d_uni FROM departments WHERE id = NEW.department_id;
    IF d_uni != NEW.university_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Instructor department must belong to the same university.';
    END IF;
END//

CREATE TRIGGER trg_instructor_dept_uni_check_update
BEFORE UPDATE ON instructors
FOR EACH ROW
BEGIN
    DECLARE d_uni INT;
    SELECT university_id INTO d_uni FROM departments WHERE id = NEW.department_id;
    IF d_uni != NEW.university_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Instructor department must belong to the same university.';
    END IF;
END//

-- Trigger: Validate course_books instructor teaches that course
CREATE TRIGGER trg_course_book_instructor_check
BEFORE INSERT ON course_books
FOR EACH ROW
BEGIN
    IF NEW.instructor_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM course_instructors WHERE course_id = NEW.course_id AND instructor_id = NEW.instructor_id) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Instructor must be assigned to this course.';
        END IF;
    END IF;
END//

DELIMITER ;
