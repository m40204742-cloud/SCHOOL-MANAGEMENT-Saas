from flask import Blueprint, jsonify
from database import get_db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/school/<int:school_id>', methods=['GET'])
def school_dashboard(school_id):
    try:
        conn = get_db()
        c = conn.cursor()

        # Get school info
        c.execute('SELECT * FROM schools WHERE id = ?', (school_id,))
        school = c.fetchone()

        if not school:
            return jsonify({'error': 'School not found'}), 404

        # Count students
        c.execute(
            'SELECT COUNT(*) as count FROM students WHERE school_id = ?', (school_id,))
        student_count = c.fetchone()['count']

        # Get fees summary
        c.execute('''SELECT 
                     SUM(f.amount) as total_owed,
                     SUM(f.paid) as total_paid
                     FROM fees f
                     JOIN students s ON f.student_id = s.id
                     WHERE s.school_id = ?''', (school_id,))
        fees_summary = c.fetchone()

        total_owed = fees_summary['total_owed'] or 0
        total_paid = fees_summary['total_paid'] or 0
        outstanding = total_owed - total_paid

        # Get defaulters (paid less than 50% of what they owe)
        c.execute('''SELECT s.id, s.name, f.amount, f.paid
                     FROM fees f
                     JOIN students s ON f.student_id = s.id
                     WHERE s.school_id = ? AND f.paid < (f.amount * 0.5)''', (school_id,))
        defaulters = c.fetchall()

        conn.close()

        return jsonify({
            'school_name': school['name'],
            'total_students': student_count,
            'total_fees_owed': total_owed,
            'total_fees_paid': total_paid,
            'total_outstanding': outstanding,
            'defaulters_count': len(defaulters),
            'defaulters': [dict(d) for d in defaulters]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
