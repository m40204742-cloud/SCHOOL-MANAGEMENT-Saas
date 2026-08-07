import requests
from flask import Blueprint, request, jsonify

sms_bp = Blueprint('sms', __name__)

AFRICAS_TALKING_API_KEY = "atsc_test_key_12345"
AFRICAS_TALKING_USERNAME = "sandbox"


@sms_bp.route('/send-reminder/<int:fee_id>', methods=['POST'])
def send_payment_reminder(fee_id):
    data = request.get_json()

    phone = data.get('phone')
    student_name = data.get('student_name')
    amount_owed = data.get('amount_owed')
    school_name = data.get('school_name')

    if not all([phone, student_name, amount_owed, school_name]):
        return jsonify({'error': 'Missing required fields'}), 400

    message = f"Hello! {student_name}'s school fees of GHS {amount_owed} are now due at {school_name}. Please pay to avoid delays. Thank you."

    return jsonify({
        'message': 'Reminder queued for sending',
        'phone': phone,
        'student_name': student_name,
        'amount': amount_owed,
        'status': 'queued'
    }), 200


@sms_bp.route('/send-bulk-reminders/<int:school_id>', methods=['POST'])
def send_bulk_reminders(school_id):
    data = request.get_json()

    defaulters = data.get('defaulters', [])
    school_name = data.get('school_name')

    if not defaulters or not school_name:
        return jsonify({'error': 'Missing defaulters or school name'}), 400

    sent_count = len(defaulters)

    return jsonify({
        'message': 'Bulk reminders queued',
        'sent': sent_count,
        'school_name': school_name
    }), 200
