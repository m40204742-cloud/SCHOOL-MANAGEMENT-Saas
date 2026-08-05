from flask import Flask, jsonify
from database import init_db
from auth import auth_bp

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')


@app.route('/')
def home():
    return jsonify({
        'message': 'School Management SaaS API',
        'status': 'Running',
        'endpoints': {
            'register': 'POST /api/auth/register',
            'login': 'POST /api/auth/login'
        }
    })


if __name__ == '__main__':
    app.run(debug=True)
