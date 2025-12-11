from flask import Flask, redirect, url_for, session
from flask_mail import Mail
import os
from datetime import timedelta
from MyFlaskapp.db import (
    create_user_table, create_activity_logs_table, create_games_table,
    create_game_access_table, create_blog_posts_table, create_blog_comments_table,
    create_profiles_table, create_otp_table, create_system_settings_table
)

def create_app():
    templates_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Email configuration
    app.config['MAIL_USERNAME'] = os.environ.get('gemaojohnreycarloarguilles@gmail.com')
    app.config['MAIL_PASSWORD'] = os.environ.get('wiqu dzsr wigj iskr')
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    
    # Initialize Flask-Mail
    mail = Mail(app)
    
    from MyFlaskapp.auth import auth_bp
    from MyFlaskapp.user import user_bp
    from MyFlaskapp.admin import admin_bp
    from MyFlaskapp.blog import blog_bp
    from MyFlaskapp.games import games_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(games_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    @app.route('/favicon.ico')
    def favicon():
        from flask import send_from_directory
        import os
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                  'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
    @app.route('/debug/session')
    def debug_session():
        from flask import jsonify
        return jsonify({
            'session_data': dict(session),
            'is_logged_in': 'user_id' in session,
            'user_info': {
                'user_id': session.get('user_id'),
                'user_name': session.get('user_name'),
                'user_role': session.get('user_role')
            } if 'user_id' in session else None
        })
    
    create_user_table()
    create_activity_logs_table()
    create_games_table()
    create_game_access_table()
    create_blog_posts_table()
    create_blog_comments_table()
    create_profiles_table()
    create_otp_table()
    create_system_settings_table()
    return app
