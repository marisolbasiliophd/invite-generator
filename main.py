from flask import Flask, render_template, request, jsonify, flash
from invite import create_invite_text
import time
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-this')

# Simple rate limiting decorator
def rate_limit(seconds=1):
    last_request_time = {}
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if request.remote_addr in last_request_time:
                time_passed = current_time - last_request_time[request.remote_addr]
                if time_passed < seconds:
                    return jsonify({'error': 'Please wait before making another request'}), 429
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

        # Validate payment related fields if cash donations are selected
        if 'cash donations welcome' in data.get('preferences', []):
            if data.get('cash_method') == 'paypal' and not data.get('paypal_link'):
                return jsonify({'error': 'PayPal link is required when PayPal method is selected'}), 400

        # Validate charity link if charity donations are selected
        if 'charity donations welcome' in data.get('preferences', []) and not data.get('charity_link'):
            return jsonify({'error': 'Charity link is required when charity donations are selected'}), 400

        # Generate invite text
        invite_text = create_invite_text(data)

        return jsonify({'invite_text': invite_text})

    except Exception as e:
        app.logger.error(f"Error generating invite: {str(e)}")
        return jsonify({'error': 'An error occurred while generating the invite'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)