import requests
from flask import Blueprint, request, jsonify
from database import get_db

paystack_bp = Blueprint('paystack', __name__)

PAYSTACK_SECRET_KEY = "sk_test_c83f779e80f6e48cc79dd3a3af4ae6f6403ae545"
PAYSTACK_PUBLIC_KEY = "pk_test_6623236a3e5f3b1a3a279c154415d3d751dec946"


@paystack_bp.route('/initialize', methods=['POST'])
def initialize_payment():
    data = request.get_json()

    fee_id = data.get('fee_id')
    email = data.get('email')
    amount = data.get('amount')

    if not all([fee_id, email, amount]):
        return jsonify({'error': 'Missing required fields'}), 400

    amount_in_kobo = int(amount * 100)

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": email,
        "amount": amount_in_kobo,
        "metadata": {
            "fee_id": fee_id
        }
    }

    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'authorization_url': data['data']['authorization_url'],
                'access_code': data['data']['access_code'],
                'reference': data['data']['reference']
            }), 200
        else:
            return jsonify({'error': 'Paystack error'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@paystack_bp.route('/verify/<reference>', methods=['GET'])
def verify_payment(reference):
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    try:
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers
        )

        if response.status_code == 200:
            payment_data = response.json()['data']

            if payment_data['status'] == 'success':
                fee_id = payment_data['metadata']['fee_id']
                amount = payment_data['amount'] / 100

                conn = get_db()
                c = conn.cursor()
                c.execute(
                    'UPDATE fees SET paid = paid + ? WHERE id = ?', (amount, fee_id))
                conn.commit()
                conn.close()

                return jsonify({
                    'message': 'Payment verified and recorded',
                    'status': 'success',
                    'amount': amount
                }), 200
            else:
                return jsonify({
                    'message': 'Payment not successful',
                    'status': payment_data['status']
                }), 400
        else:
            return jsonify({'error': 'Verification failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400
