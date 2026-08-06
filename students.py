from flask import Blueprint, request, jsonify
from database import get_db

students_bp = Blueprint('students', __name__)


@students_bp.route('/add', methods=['POST'])
def add_student():
    data = request.get_json()

    school_id = data.get('school_id')
    name = data.get('name')
    class_name = data.get('class')
    fee_amount = data.get('fee_amount')

    if not all([school_id, name, fee_amount]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('''INSERT INTO students (school_id, name, class, fee_amount) 
                     VALUES (?, ?, ?, ?)''',
                  (school_id, name, class_name, fee_amount))
        conn.commit()
        student_id = c.lastrowid
        conn.close()

        return jsonify({
            'message': 'Student added successfully',
            'student_id': student_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@students_bp.route('/list/<int:school_id>', methods=['GET'])
def list_students(school_id):
    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT * FROM students WHERE school_id = ?', (school_id,))
        students = c.fetchall()
        conn.close()

        return jsonify({
            'students': [dict(s) for s in students],
            'total': len(students)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@students_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        student = c.fetchone()
        conn.close()

        if not student:
            return jsonify({'error': 'Student not found'}), 404

        return jsonify(dict(student)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
