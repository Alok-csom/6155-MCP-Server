import sqlite3

def init_database():
    conn = sqlite3.connect("student_records.db")
    cursor = conn.cursor()

    # 1. Students Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL
        );
    """)

    # 2. Courses Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            course_name TEXT NOT NULL
        );
    """)

    # 3. Grades Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            numeric_score REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (student_id),
            FOREIGN KEY (course_id) REFERENCES courses (course_id)
        );
    """)

    # 4. Grade Scale Mapping Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grade_scale (
            min_score REAL,
            max_score REAL,
            letter_grade TEXT PRIMARY KEY,
            gpa_points REAL
        );
    """)

    # Insert Seed Records
    cursor.executemany("INSERT OR REPLACE INTO grade_scale VALUES (?, ?, ?, ?);", [
        (90.0, 100.0, 'A', 4.0),
        (80.0, 89.99, 'B', 3.0),
        (70.0, 79.99, 'C', 2.0),
        (60.0, 69.99, 'D', 1.0),
        (0.0,  59.99, 'F', 0.0)
    ])

    cursor.executemany("INSERT INTO students (full_name, email) VALUES (?, ?);", [
        ("Alice Smith", "alice@univ.edu"),
        ("Bob Jones", "bob@univ.edu"),
        ("Charlie Brown", "charlie@univ.edu")
    ])

    cursor.executemany("INSERT INTO courses (course_code, course_name) VALUES (?, ?);", [
        ("CS101", "Introduction to Computer Science"),
        ("MATH201", "Linear Algebra")
    ])

    cursor.executemany("INSERT INTO grades (student_id, course_id, numeric_score) VALUES (?, ?, ?);", [
        (1, 1, 94.5), # Alice - CS101 (A)
        (1, 2, 82.0), # Alice - MATH201 (B)
        (2, 1, 76.0), # Bob - CS101 (C)
        (2, 2, 58.5)  # Bob - MATH201 (F)
    ])

    conn.commit()
    conn.close()
    print("Database student_records.db initialized and seeded successfully!")

if __name__ == "__main__":
    init_database()