from flask import Flask, jsonify
from database import init_db
from auth import auth_bp
from students import students_bp
from fees import fees_bp
from dashboard import dashboard_bp

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(students_bp, url_prefix='/api/students')
app.register_blueprint(fees_bp, url_prefix='/api/fees')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')


@app.route('/')
def home():
    return jsonify({
        'message': 'School Management SaaS API',
        'status': 'Running',
        'endpoints': {
            'auth': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login'
            },
            'students': {
                'add': 'POST /api/students/add',
                'list': 'GET /api/students/list/<school_id>',
                'get': 'GET /api/students/<student_id>'
            },
            'fees': {
                'create': 'POST /api/fees/create',
                'get_school_fees': 'GET /api/fees/school/<school_id>',
                'pay': 'POST /api/fees/pay/<fee_id>'
            },
            'dashboard': {
                'school_dashboard': 'GET /api/dashboard/school/<school_id>'
            }
        }
    })


if __name__ == '__main__':
    app.run(debug=True)
