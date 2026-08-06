from flask import Blueprint, request, jsonify
from database import get_db

fees_bp = Blueprint('fees', __name__)


@fees_bp.route('/create', methods=['POST'])
def create_invoice():
    data = request.get_json()

    student_id = data.get('student_id')
    amount = data.get('amount')
    term = data.get('term')
    due_date = data.get('due_date')

    if not all([student_id, amount]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('''INSERT INTO fees (student_id, amount, term, due_date) 
                     VALUES (?, ?, ?, ?)''',
                  (student_id, amount, term, due_date))
        conn.commit()
        fee_id = c.lastrowid
        conn.close()

        return jsonify({
            'message': 'Invoice created',
            'fee_id': fee_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@fees_bp.route('/school/<int:school_id>', methods=['GET'])
def get_school_fees(school_id):
    try:
        conn = get_db()
        c = conn.cursor()

        # Get all fees for this school's students
        c.execute('''SELECT f.*, s.name as student_name 
                     FROM fees f 
                     JOIN students s ON f.student_id = s.id 
                     WHERE s.school_id = ?''', (school_id,))
        fees = c.fetchall()

        # Calculate totals
        total_owed = sum([f['amount'] for f in fees])
        total_paid = sum([f['paid'] for f in fees])
        total_outstanding = total_owed - total_paid

        conn.close()

        return jsonify({
            'fees': [dict(f) for f in fees],
            'total_owed': total_owed,
            'total_paid': total_paid,
            'total_outstanding': total_outstanding
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@fees_bp.route('/pay/<int:fee_id>', methods=['POST'])
def pay_fee(fee_id):
    data = request.get_json()
    amount_paid = data.get('amount')

    if not amount_paid:
        return jsonify({'error': 'Amount required'}), 400

    try:
        conn = get_db()
        c = conn.cursor()

        c.execute('SELECT paid FROM fees WHERE id = ?', (fee_id,))
        fee = c.fetchone()

        if not fee:
            return jsonify({'error': 'Fee not found'}), 404

        new_paid = fee['paid'] + amount_paid
        c.execute('UPDATE fees SET paid = ? WHERE id = ?', (new_paid, fee_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Payment recorded', 'new_paid': new_paid}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
