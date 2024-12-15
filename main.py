from flask import Flask, render_template, request, jsonify
from invite import create_invite_text, THEME_ELEMENTS
import time
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-this')

def validate_theme_data(data):
    """Validate theme-related data"""
    if not data.get('theme'):
        return "Theme is required"

    theme = data['theme']
    if theme.startswith('other:'):
        custom_theme = theme.replace('other:', '').strip()
        if not custom_theme:
            return "Custom theme cannot be empty"
    elif theme != 'none' and theme not in THEME_ELEMENTS:
        return f"Invalid theme selected: {theme}"

    return None

def validate_required_fields(data):
    """Validate all required fields are present and valid"""
    required_fields = {
        'celebrant_name': str,
        'celebration_type': str,
        'date': str,
        'time': str,
        'location': str,
        'style': str,
        'emoji_level': str,
        'length': str,
        'gift_emphasis_level': str
    }

    for field, field_type in required_fields.items():
        if field not in data:
            return f"Missing required field: {field}"
        if not isinstance(data[field], field_type):
            return f"Invalid type for field {field}"

    return None

# Rate limiting with cleanup
def rate_limit(seconds=1):
    last_request_time = {}
    max_entries = 1000  # Prevent memory issues

    def cleanup_old_entries():
        current_time = time.time()
        expired_keys = [
            k for k, v in last_request_time.items() 
            if current_time - v > seconds * 2
        ]
        for k in expired_keys:
            last_request_time.pop(k, None)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_time = time.time()

            # Cleanup old entries if dict is too large
            if len(last_request_time) > max_entries:
                cleanup_old_entries()

            if request.remote_addr in last_request_time:
                time_passed = current_time - last_request_time[request.remote_addr]
                if time_passed < seconds:
                    return jsonify({
                        'error': 'Please wait a moment before generating another invitation'
                    }), 429

            last_request_time[request.remote_addr] = current_time
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-invite', methods=['POST'])
@rate_limit(1)  # Rate limit: 1 request per second
def generate_invite():
    try:
        # Get form data
        data = request.json

        # Validate required fields
        error = validate_required_fields(data)
        if error:
            return jsonify({'error': error}), 400

        # Validate theme
        error = validate_theme_data(data)
        if error:
            return jsonify({'error': error}), 400

        # Validate payment related fields
        if 'cash donations welcome' in data.get('preferences', []):
            if data.get('cash_method') == 'paypal' and not data.get('paypal_link'):
                return jsonify({
                    'error': 'PayPal link is required when PayPal method is selected'
                }), 400

        # Validate charity link
        if 'charity donations welcome' in data.get('preferences', []) and not data.get('charity_link'):
            return jsonify({
                'error': 'Charity link is required when charity donations are selected'
            }), 400

        # Generate invite text
        invite_text = create_invite_text(data)
        return jsonify({'invite_text': invite_text})

    except ValueError as e:
        app.logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error generating invite: {str(e)}")
        return jsonify({'error': 'An error occurred while generating the invitation'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)