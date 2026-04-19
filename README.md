# 📚 GyanPustak — Online Textbook Store

**GyanPustak** is a full-stack web application for buying and renting textbooks online. It supports **new**, **used**, and **ebook** formats with a robust multi-role system designed for educational institutions.

---

## 🌟 Project Overview

GyanPustak provides a seamless platform where students can browse, buy, or rent textbooks while administrators manage inventory, courses, and support operations. The platform features four distinct user roles : **Student**, **Support**, **Admin**, and **Super Admin** : each with tailored dashboards and permissions.

---

## 🚀 Features

### 👨‍🎓 Student
- Browse books with **smart search**, filters (category, format, type, price range), and **pagination**
- View detailed book information including authors, keywords, and course associations
- **Add to cart** : buy and rent items handled separately
- **Place orders** with shipping and payment options
- **Request order cancellation** (before completion)
- **Track order status** (new → processed → awaiting shipping → shipped → completed)
- **Write reviews** for completed orders
- **Create support tickets** for issues
- **Password reset** and profile management

### 🛠️ Support
- View and **handle cancellation requests** (approve/reject)
- **Create tickets** on behalf of students
- **Assign tickets to admin** for resolution
- **Manage and resolve tickets** with status tracking and history

### 📦 Admin
- **Manage books** : add, edit, delete books with full metadata (authors, keywords, subcategories)
- **Manage inventory** : track stock quantities
- **Manage universities**, departments, courses, and instructors
- **Link books to courses** (required/recommended)
- **Handle assigned tickets** and update their status

### 👑 Super Admin
- **Add employees** (admin and support roles only)
- **View all employees** and manage the workforce
- **Full system control** : access to all admin features
- ⚠️ **Only ONE Super Admin exists** in the system (enforced by database trigger)

### ⚙️ System Features
- **Smart search** with keyword matching across titles, authors, ISBNs, and keywords
- **Role-based access control** via decorators and session management
- **Form validation** on both client and server side
- **SQL error handling** with meaningful error messages
- **Order status automation** via database triggers
- **Ticket history** : automatic logging of status changes
- **Database triggers** for data integrity (university consistency, single cart enforcement, review validation, etc.)

---

## 🛠️ Tech Stack

| Layer       | Technology        |
|-------------|-------------------|
| **Frontend**  | HTML, CSS         |
| **Backend**   | Python (Flask)    |
| **Database**  | MySQL             |
| **Auth**      | bcrypt (password hashing) |
| **DB Driver** | PyMySQL           |

---

## 📁 Project Structure

```
gyanpustak/
├── app.py                  # Application entry point
├── config.py               # Configuration & environment variables
├── requirements.txt        # Python dependencies
│
├── database/
│   ├── db.py               # Database connection helper
│   ├── schema.sql          # Complete database schema with triggers
│   └── sample_data.sql     # Sample data for testing
│
├── models/
│   ├── user.py             # User model (login, register, password reset)
│   ├── book.py             # Book model (CRUD, search, filters)
│   ├── student.py          # Student-specific queries
│   └── employee.py         # Employee-specific queries
│
├── routes/
│   ├── auth.py             # Authentication routes (login, register, logout)
│   ├── student.py          # Student dashboard & actions
│   ├── support.py          # Support dashboard & ticket management
│   ├── admin.py            # Admin dashboard & book/course management
│   ├── super_admin.py      # Super Admin employee management
│   └── superadmin.py       # Additional super admin routes
│
├── services/
│   ├── cart_service.py     # Cart operations
│   ├── order_service.py    # Order processing
│   └── ticket_service.py   # Ticket management
│
├── templates/
│   ├── auth/               # Login & registration pages
│   ├── student/            # Student dashboard & views
│   ├── admin/              # Admin dashboard & management pages
│   ├── support/            # Support dashboard & ticket views
│   ├── super_admin/        # Super admin views
│   ├── shared/             # Base templates & layout
│   └── errors/             # 404 & 500 error pages
│
├── static/
│   ├── css/style.css       # Application styles
│   └── images/             # Static images (placeholders)
│
└── utils/
    ├── auth.py             # Authentication helpers
    ├── helpers.py          # Utility functions
    ├── decorators.py       # Role-based access decorators
    └── validators.py       # Input validation
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your_secret_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=gyanpustak
MYSQL_PORT=3306
```

---

## ⚡ Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

---

### 🐧 Linux Setup

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip mysql-server
   ```

2. **Clone the repository and install Python packages:**
   ```bash
   cd gyanpustak
   pip install -r requirements.txt
   ```

3. **Setup the database:**
   ```bash
   mysql -u root -p < database/schema.sql
   ```

4. **Load sample data (optional):**
   ```bash
   mysql -u root -p gyanpustak < database/sample_data.sql
   ```

5. **Create `.env` file** (see Environment Variables section above)

6. **Run the application:**
   ```bash
   python app.py
   ```

7. **Access the app** at `http://localhost:5000`

---

### 🪟 Windows Setup

1. **Install Python** from [python.org](https://python.org) (check "Add to PATH")

2. **Install MySQL** from [dev.mysql.com](https://dev.mysql.com/downloads/installer/)

3. **Install Python packages:**
   ```cmd
   cd gyanpustak
   pip install -r requirements.txt
   ```

4. **Setup the database** — Open MySQL CLI:
   ```sql
   CREATE DATABASE gyanpustak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   USE gyanpustak;
   source C:/path/to/project/database/schema.sql;
   ```

5. **Load sample data (optional):**
   ```sql
   USE gyanpustak;
   source C:/path/to/project/database/sample_data.sql;
   ```

6. **Create `.env` file** (see Environment Variables section above)

7. **Run the application:**
   ```cmd
   python app.py
   ```

8. **Access the app** at `http://localhost:5000`

---

## 👥 Sample Login Credentials

| Role         | Email                        | Password         |
|--------------|------------------------------|------------------|
| Super Admin  | superadmin@gyanpustak.com    | SuperAdmin@123   |
| Admin 1      | admin1@gyanpustak.com        | Admin@123       |
| Admin 2      | admin2@gyanpustak.com        | Admin@123       |
| Support 1    | support1@gyanpustak.com      | Support@123     |
| Support 2    | support2@gyanpustak.com      | Support@123     |
| Student 1    | student1@example.com      | Student@123     |
| Student 2    | student2@example.com      | Student@123     |
| Student 3    | student3@example.com      | Student@123     |

---

## 📊 Database Schema

The database consists of **25+ tables** with proper normalization, foreign keys, and triggers:

- **Core:** `users`, `employee_profiles`, `student_profiles`
- **Academic:** `universities`, `departments`, `courses`, `instructors`
- **Books:** `books`, `authors`, `keywords`, `categories`, `book_authors`, `book_keywords`
- **Commerce:** `carts`, `cart_items`, `orders`, `order_items`, `order_cancellations`
- **Support:** `tickets`, `ticket_history`
- **Reviews:** `reviews`
- **Linking:** `course_departments`, `course_instructors`, `course_books`

### Key Triggers
- Prevent multiple Super Admins
- Enforce single cart per student
- Auto-log ticket status changes
- Validate reviews only for completed orders
- University consistency checks for courses, instructors, and departments

---

## 📄 License

This project is developed for educational purposes.
