from flask import Blueprint, request, jsonify, redirect, url_for, render_template, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # Check if user exists
    existing_user = User.get_by_email(email, current_app.config['DATABASE'])
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    user = User.create(email, password, full_name, current_app.config['DATABASE'])
    
    if user:
        login_user(user)
        return jsonify({'success': True, 'redirect': '/'}), 201
    
    return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.get_by_email(email, current_app.config['DATABASE'])
    
    if user and user.check_password(password):
        login_user(user, remember=True)
        return jsonify({'success': True, 'redirect': '/'}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing.index'))

@bp.route('/user')
@login_required
def get_current_user():
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'full_name': current_user.full_name,
        'plan': current_user.plan
    })