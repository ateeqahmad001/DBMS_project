USE gyanpustak;

-- ============ USERS ============
INSERT INTO users (email, password_hash, role) VALUES
('superadmin@gyanpustak.com', '$2b$12$AaReVMQV1GAkFO/tF0mk0evVo.aDLUi1W8rozpDY6/ZycXhqSaLOW', 'superadmin'),
('admin1@gyanpustak.com', '$2b$12$3A.Oc5HhRPgAjQwx9Z.wBOVc7J7B4KcFxLVTsCG9c2YaNJ.iFXqPy', 'admin'),
('admin2@gyanpustak.com', '$2b$12$3A.Oc5HhRPgAjQwx9Z.wBOVc7J7B4KcFxLVTsCG9c2YaNJ.iFXqPy', 'admin'),
('support1@gyanpustak.com', '$2b$12$fj8QF1xIrR93IhUL6QFoyeXWG7ICUA6m1TgB5GbrOqB45RgqD2Cya', 'support'),
('support2@gyanpustak.com', '$2b$12$fj8QF1xIrR93IhUL6QFoyeXWG7ICUA6m1TgB5GbrOqB45RgqD2Cya', 'support'),
('student1@example.com', '$2b$12$a/TlPM0i6R0mz9Qu5a8PfeHQHI1z/hCQeQygGHJD4GBG.fUEygTMO', 'student'),
('student2@example.com', '$2b$12$a/TlPM0i6R0mz9Qu5a8PfeHQHI1z/hCQeQygGHJD4GBG.fUEygTMO', 'student'),
('student3@example.com', '$2b$12$a/TlPM0i6R0mz9Qu5a8PfeHQHI1z/hCQeQygGHJD4GBG.fUEygTMO', 'student'),
('student4@example.com', '$2b$12$a/TlPM0i6R0mz9Qu5a8PfeHQHI1z/hCQeQygGHJD4GBG.fUEygTMO', 'student'),
('student5@example.com', '$2b$12$a/TlPM0i6R0mz9Qu5a8PfeHQHI1z/hCQeQygGHJD4GBG.fUEygTMO', 'student');

-- ============ EMPLOYEE PROFILES ============
INSERT INTO employee_profiles (user_id, employee_id, first_name, last_name, gender, salary, aadhaar, phone, address) VALUES
(2, 'EMP001', 'Rajesh', 'Verma', 'male', 75000.00, '123456789012', '9988776655', '10 Admin Block, Delhi'),
(3, 'EMP002', 'Sunita', 'Kapoor', 'female', 72000.00, '123456789013', '9988776656', '11 Admin Block, Delhi'),
(4, 'EMP003', 'Manoj', 'Tiwari', 'male', 55000.00, '123456789014', '9988776657', '20 Support Wing, Delhi'),
(5, 'EMP004', 'Kavita', 'Saxena', 'female', 53000.00, '123456789015', '9988776658', '21 Support Wing, Delhi');

-- ============ UNIVERSITIES ============
INSERT INTO universities (name, address, rep_first_name, rep_last_name, rep_email, rep_phone) VALUES
('IIT BBS', 'Jatni, Khurda, Odisha 752050', 'Ramesh', 'Panda', 'rep@iitbbs.ac.in', '9900110011'),
('Delhi University', 'University Rd, New Delhi 110007', 'Anil', 'Sharma', 'rep@du.ac.in', '9900110012'),
('IIT Bombay', 'Powai, Mumbai 400076', 'Suresh', 'Kulkarni', 'rep@iitb.ac.in', '9900110013'),
('IISc Bangalore', 'CV Raman Rd, Bangalore 560012', 'Mohan', 'Rao', 'rep@iisc.ac.in', '9900110014'),
('IIIT Hyderabad', 'Gachibowli, Hyderabad 500032', 'Lakshmi', 'Devi', 'rep@iiith.ac.in', '9900110015');

-- ============ DEPARTMENTS ============
INSERT INTO departments (name, university_id) VALUES
('Computer Science', 1), ('Electrical Engineering', 1), ('Mechanical Engineering', 1),
('Computer Science', 2), ('Physics', 2), ('Mathematics', 2),
('Computer Science', 3), ('Electronics', 3), ('Mechanical', 3),
('Physics', 4), ('Chemistry', 4),
('Computer Science', 5), ('Data Science', 5);

-- ============ STUDENT PROFILES ============
INSERT INTO student_profiles (user_id, first_name, last_name, phone, dob, address, university_id, department_id, major, student_status, year) VALUES
(6, 'Rahul', 'Sharma', '9876543210', '2002-05-15', '100 Student Lane, Delhi', 1, 1, 'Computer Science', 'UG', 3),
(7, 'Priya', 'Patel', '9876543211', '2001-08-20', '101 Student Lane, Mumbai', 3, 7, 'Computer Science', 'UG', 4),
(8, 'Ankit', 'Singh', '9876543212', '2003-01-10', '102 Student Lane, Bangalore', 4, 10, 'Physics', 'PG', 1),
(9, 'Sneha', 'Gupta', '9876543213', '2002-11-25', '103 Student Lane, Hyderabad', 5, 12, 'Computer Science', 'UG', 2),
(10, 'Vikram', 'Reddy', '9876543214', '2001-03-30', '104 Student Lane, Delhi', 2, 4, 'Computer Science', 'PG', 2);

-- ============ INSTRUCTORS ============
INSERT INTO instructors (first_name, last_name, email, university_id, department_id) VALUES
('Amit', 'Kumar', 'akumar@iitbbs.ac.in', 1, 1),
('Bikash', 'Singh', 'bsingh@iitbbs.ac.in', 1, 2),
('Chandan', 'Rao', 'crao@du.ac.in', 2, 4),
('Deepa', 'Nair', 'dnair@iitb.ac.in', 3, 7),
('Esha', 'Pillai', 'epillai@iisc.ac.in', 4, 10),
('Farhan', 'Jha', 'fjha@iiith.ac.in', 5, 12),
('Pranav', 'Mishra', 'pmishra@iitbbs.ac.in', 1, 1);

-- ============ COURSES ============
INSERT INTO courses (name, code, university_id, year, semester) VALUES
('Data Structures', 'CS201', 1, 2024, 'Fall'),
('Algorithms', 'CS301', 1, 2024, 'Spring'),
('Operating Systems', 'CS302', 1, 2024, 'Fall'),
('Quantum Physics', 'PH301', 2, 2024, 'Fall'),
('Digital Electronics', 'EC201', 3, 2024, 'Spring'),
('Solid State Physics', 'PH401', 4, 2024, 'Spring'),
('Machine Learning', 'CS501', 5, 2024, 'Fall');

-- ============ COURSE-DEPARTMENT LINKS ============
INSERT INTO course_departments (course_id, department_id) VALUES
(1, 1), (2, 1), (3, 1),
(4, 5), (5, 8),
(6, 10), (7, 12), (7, 13);

-- ============ COURSE-INSTRUCTOR LINKS ============
INSERT INTO course_instructors (course_id, instructor_id) VALUES
(1, 1), (1, 7), (2, 1), (3, 1),
(4, 3), (5, 4),
(6, 5), (7, 6);

-- ============ CATEGORIES ============
INSERT INTO categories (name) VALUES
('Computer Science'), ('Physics'), ('Mathematics'),
('Chemistry'), ('Engineering'), ('Electronics'),
('Data Science'), ('Literature'), ('Business'),
('Biology');

-- ============ AUTHORS ============
INSERT INTO authors (name) VALUES
('Cormen'), ('Leiserson'), ('Rivest'), ('Stein'),
('Silberschatz'), ('Galvin'), ('Gagne'), ('Korth'), ('Sudarshan'),
('H.C. Verma'), ('B.S. Grewal'),
('Clayden'), ('Greeves'), ('Warren'),
('M. Morris Mano'), ('Jake VanderPlas'), ('Tom Mitchell'),
('Aho'), ('Lam'), ('Sethi'), ('Ullman'),
('Frank White'), ('Sheldon Axler');

-- ============ BOOKS ============
INSERT INTO books (title, isbn, publisher, publication_date, edition, language, format, book_type, purchase_option, buy_price, rent_price, quantity, category_id) VALUES
('Introduction to Algorithms', '9780262033848', 'MIT Press', '2009-07-31', '3rd', 'English', 'hardcover', 'new', 'both', 599.00, 99.00, 50, 1),
('Operating System Concepts', '9781119800361', 'Wiley', '2021-03-01', '10th', 'English', 'paperback', 'new', 'both', 499.00, 79.00, 40, 1),
('Database System Concepts', '9780078022159', 'McGraw Hill', '2019-02-01', '7th', 'English', 'paperback', 'new', 'buy', 549.00, NULL, 35, 1),
('Concepts of Physics Vol 1', '9788177091878', 'Bharati Bhawan', '2018-01-01', '2nd', 'English', 'paperback', 'new', 'both', 399.00, 59.00, 60, 2),
('Engineering Mathematics', '9789332571686', 'Khanna Publishers', '2017-01-01', '44th', 'English', 'paperback', 'used', 'buy', 250.00, NULL, 25, 3),
('Organic Chemistry', '9780199270293', 'Oxford', '2012-03-01', '2nd', 'English', 'hardcover', 'new', 'both', 699.00, 109.00, 20, 4),
('Digital Design', '9780132774208', 'Pearson', '2013-01-01', '5th', 'English', 'paperback', 'new', 'buy', 450.00, NULL, 30, 6),
('Python for Data Science', '9781491957660', 'OReilly', '2016-11-01', '1st', 'English', 'ebook', 'new', 'buy', 349.00, NULL, 999, 7),
('Machine Learning', '9780070702141', 'McGraw Hill', '1997-03-01', '1st', 'English', 'paperback', 'used', 'both', 299.00, 49.00, 15, 7),
('Compiler Design', '9780321486813', 'Pearson', '2006-08-01', '2nd', 'English', 'hardcover', 'new', 'buy', 549.00, NULL, 20, 1),
('Fluid Mechanics', '9780073398273', 'McGraw Hill', '2015-01-01', '8th', 'English', 'paperback', 'new', 'both', 479.00, 75.00, 25, 5),
('Linear Algebra Done Right', '9783319110790', 'Springer', '2015-01-01', '3rd', 'English', 'paperback', 'new', 'both', 399.00, 65.00, 30, 3);

-- ============ BOOK-AUTHORS (M:N) ============
INSERT INTO book_authors (book_id, author_id) VALUES
(1,1),(1,2),(1,3),(1,4),
(2,5),(2,6),(2,7),
(3,5),(3,8),(3,9),
(4,10),
(5,11),
(6,12),(6,13),(6,14),
(7,15),
(8,16),
(9,17),
(10,18),(10,19),(10,20),(10,21),
(11,22),
(12,23);

-- ============ KEYWORDS ============
INSERT INTO keywords (name) VALUES
('algorithms'),('data structures'),('programming'),
('OS'),('operating systems'),('processes'),
('database'),('SQL'),('DBMS'),
('physics'),('mechanics'),('thermodynamics'),
('mathematics'),('calculus'),('engineering'),
('chemistry'),('organic'),('reactions'),
('digital'),('logic'),('electronics'),
('python'),('data science'),('numpy'),
('ML'),('AI'),('machine learning'),
('compiler'),('parsing'),('automata'),
('fluids'),('linear algebra');

-- ============ BOOK-KEYWORDS (M:N) ============
INSERT INTO book_keywords (book_id, keyword_id) VALUES
(1,1),(1,2),(1,3),
(2,4),(2,5),(2,6),
(3,7),(3,8),(3,9),
(4,10),(4,11),(4,12),
(5,13),(5,14),(5,15),
(6,16),(6,17),(6,18),
(7,19),(7,20),(7,21),
(8,22),(8,23),(8,24),
(9,25),(9,26),(9,27),
(10,28),(10,29),(10,30),
(11,31),(11,11),(11,15),
(12,32),(12,13);

-- ============ COURSE-BOOK LINKS ============
INSERT INTO course_books (course_id, book_id, link_type, year, semester, instructor_id) VALUES
(1, 1, 'required', 2024, 'Fall', 1),
(2, 1, 'required', 2024, 'Spring', 1),
(3, 2, 'required', 2024, 'Fall', 1),
(4, 4, 'required', 2024, 'Fall', 3),
(5, 7, 'required', 2024, 'Spring', 4),
(6, 4, 'recommended', 2024, 'Spring', 5),
(7, 9, 'required', 2024, 'Fall', 6);

-- ============ CARTS ============
INSERT INTO carts (student_id) VALUES (6),(7),(8),(9),(10);
