from flask import Blueprint, request, jsonify
from database import get_db
import hashlib

auth_bp = Blueprint('auth', __name__)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    school_name = data.get('school_name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')

    if not all([school_name, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('INSERT INTO schools (name, email, password, phone) VALUES (?, ?, ?, ?)',
                  (school_name, email, hash_password(password), phone))
        conn.commit()
        conn.close()

        return jsonify({'message': 'School registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    conn = get_db()
    c = conn.cursor()

    c.execute('SELECT * FROM schools WHERE email = ?', (email,))
    school = c.fetchone()
    conn.close()

    if school and school['password'] == hash_password(password):
        return jsonify({
            'message': 'Login successful',
            'school_id': school['id'],
            'school_name': school['name']
        }), 200

    return jsonify({'error': 'Invalid email or password'}), 401
