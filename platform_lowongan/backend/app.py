from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Import config
from config import Config

# Import models
from models import db, User, Perusahaan, Lowongan, Lamaran

# Import blueprints
from admin.routes import admin_bp
from pencari_kerja.routes import pencari_kerja_bp
from perusahaan.routes import perusahaan_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'pencari_kerja.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(pencari_kerja_bp, url_prefix='/pencari_kerja')
    app.register_blueprint(perusahaan_bp, url_prefix='/perusahaan')
    
    @app.route('/')
    def index():
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'pencari_kerja':
                return redirect(url_for('pencari_kerja.dashboard'))
            elif user.role == 'perusahaan':
                return redirect(url_for('perusahaan.dashboard'))
        return render_template('index.html')
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('Anda telah logout.', 'success')
        return redirect(url_for('index'))
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)