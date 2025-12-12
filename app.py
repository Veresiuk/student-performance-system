from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Конфігурація підключення до MySQL
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "Vv/20072205",   # заміни на свій пароль
    "database": "student_performance",
    "charset": "utf8mb4"
}

# Функція для створення нового з’єднання
def get_connection():
    return mysql.connector.connect(**db_config)

# ------------------- ROUTES -------------------

@app.route("/students")
def get_students():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id, s.full_name, s.group_name, f.name AS faculty
        FROM students s
        JOIN faculties f ON s.faculty_id = f.id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/faculties")
def get_faculties():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM faculties")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/subjects")
def get_subjects():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM subjects")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/faculty-rating")
def get_faculty_rating():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.id, f.name AS faculty_name, AVG(g.grade) AS avg_grade
        FROM faculties f
        JOIN students s ON f.id = s.faculty_id
        JOIN grades g ON s.id = g.student_id
        GROUP BY f.id, f.name
        ORDER BY avg_grade DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/students/<int:student_id>/performance")
def get_student_performance(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Вибираємо всі оцінки студента
    cursor.execute("""
        SELECT sub.name AS subject, g.grade, g.date_passed
        FROM grades g
        JOIN subjects sub ON g.subject_id = sub.id
        WHERE g.student_id = %s
    """, (student_id,))
    grades = cursor.fetchall()

    # Рахуємо середній бал
    cursor.execute("""
        SELECT AVG(grade) AS avg_grade
        FROM grades
        WHERE student_id = %s
    """, (student_id,))
    avg = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify({
        "grades": grades,
        "average": avg["avg_grade"]
    })

# ------------------- MAIN -------------------

if __name__ == "__main__":
    app.run(debug=True)
