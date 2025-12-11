from flask import render_template, session, redirect, url_for, flash, request, jsonify
from . import admin_bp
from MyFlaskapp.utils import login_required
from MyFlaskapp import db
import mysql.connector
from datetime import datetime, timedelta
import json


@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if session.get('user_role') != 'admin':
        flash('Access denied. This area is for admins only.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get dashboard statistics
    stats = get_dashboard_stats()
    return render_template('admin/admin_dashboard.html', stats=stats)

# User Management Routes
@admin_bp.route('/users')
@login_required
def users_list():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    role_filter = request.args.get('role', '')
    
    users = get_users_filtered(search, status_filter, role_filter)
    return render_template('admin/users.html', users=users, search=search, status_filter=status_filter, role_filter=role_filter)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        update_user_data(user_id, request.form)
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users_list'))
    
    user = get_user_by_id(user_id)
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/toggle_status')
@login_required
def toggle_user_status(user_id):
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    toggle_user_status_db(user_id)
    flash('User status updated.', 'success')
    return redirect(url_for('admin.users_list'))

# Content Management Routes
@admin_bp.route('/blog/posts')
@login_required
def blog_posts():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    posts = get_all_blog_posts()
    return render_template('admin/blog_posts.html', posts=posts)

@admin_bp.route('/blog/create', methods=['GET', 'POST'])
@login_required
def create_blog_post():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags', '')
        status = request.form.get('status', 'draft')
        featured_image = request.form.get('featured_image', '')
        
        if not title or not content:
            flash('Title and content are required', 'danger')
            return render_template('admin/create_blog_post.html')
        
        if create_blog_post_db(title, content, session.get('user_id'), status, tags, featured_image):
            flash('Blog post created successfully!', 'success')
            return redirect(url_for('admin.blog_posts'))
        else:
            flash('Error creating blog post', 'danger')
    
    return render_template('admin/create_blog_post.html')

@admin_bp.route('/blog/posts/<int:post_id>/toggle_status')
@login_required
def toggle_post_status(post_id):
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    toggle_blog_post_status(post_id)
    flash('Post status updated.', 'success')
    return redirect(url_for('admin.blog_posts'))

@admin_bp.route('/blog/comments')
@login_required
def blog_comments():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    comments = get_all_blog_comments()
    return render_template('admin/blog_comments.html', comments=comments)

@admin_bp.route('/blog/comments/<int:comment_id>/moderate', methods=['POST'])
@login_required
def moderate_comment(comment_id):
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    action = request.form.get('action')
    moderate_blog_comment(comment_id, action)
    flash('Comment moderated.', 'success')
    return redirect(url_for('admin.blog_comments'))

# Game Management Routes
@admin_bp.route('/games')
@login_required
def games_management():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    games = get_all_games()
    return render_template('admin/games.html', games=games)

@admin_bp.route('/games/<int:game_id>/toggle')
@login_required
def toggle_game(game_id):
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    toggle_game_status(game_id)
    flash('Game status updated.', 'success')
    return redirect(url_for('admin.games_management'))

@admin_bp.route('/games/access')
@login_required
def game_access():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    access_list = get_game_access_list()
    return render_template('admin/game_access.html', access_list=access_list)

@admin_bp.route('/games/access/<string:user_id>/<string:game_code>/toggle')
@login_required
def toggle_game_access(user_id, game_code):
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    toggle_game_access_db(user_id, game_code)
    flash('Game access updated.', 'success')
    return redirect(url_for('admin.game_access'))

# System Administration Routes
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def system_settings():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        update_system_settings(request.form)
        flash('Settings updated.', 'success')
        return redirect(url_for('admin.system_settings'))
    
    settings = get_system_settings()
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/activity_logs')
@login_required
def activity_logs():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    logs = get_activity_logs()
    return render_template('admin/activity_logs.html', logs=logs)

@admin_bp.route('/otp')
@login_required
def otp_management():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    otp_list = get_otp_list()
    return render_template('admin/otp.html', otp_list=otp_list)

# Analytics Routes
@admin_bp.route('/analytics')
@login_required
def analytics():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    analytics_data = get_analytics_data()
    return render_template('admin/analytics.html', analytics=analytics_data)

# Security Routes
@admin_bp.route('/security')
@login_required
def security_monitoring():
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    security_data = get_security_data()
    return render_template('admin/security.html', security=security_data)

# Database Helper Functions
def get_dashboard_stats():
    conn = db.get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # User statistics
        cursor.execute("SELECT COUNT(*) as total_users FROM user_tb")
        total_users = cursor.fetchone()['total_users']
        
        cursor.execute("SELECT COUNT(*) as active_users FROM user_tb WHERE status = 'active'")
        active_users = cursor.fetchone()['active_users']
        
        cursor.execute("SELECT COUNT(*) as pending_users FROM user_tb WHERE status = 'pending'")
        pending_users = cursor.fetchone()['pending_users']
        
        # Blog statistics
        cursor.execute("SELECT COUNT(*) as total_posts FROM blog_posts")
        total_posts = cursor.fetchone()['total_posts']
        
        cursor.execute("SELECT COUNT(*) as published_posts FROM blog_posts WHERE status = 'published'")
        published_posts = cursor.fetchone()['published_posts']
        
        cursor.execute("SELECT COUNT(*) as pending_comments FROM blog_comments WHERE status = 'pending'")
        pending_comments = cursor.fetchone()['pending_comments']
        
        # Game statistics
        cursor.execute("SELECT COUNT(*) as active_games FROM games WHERE is_active = TRUE")
        active_games = cursor.fetchone()['active_games']
        
        cursor.execute("SELECT COUNT(*) as total_game_access FROM game_access WHERE access_granted = TRUE")
        total_game_access = cursor.fetchone()['total_game_access']
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'pending_users': pending_users,
            'total_posts': total_posts,
            'published_posts': published_posts,
            'pending_comments': pending_comments,
            'active_games': active_games,
            'total_game_access': total_game_access
        }
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return {}
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_users_filtered(search, status_filter, role_filter):
    conn = db.get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM user_tb WHERE 1=1"
        params = []
        
        if search:
            query += " AND (username LIKE %s OR firstname LIKE %s OR lastname LIKE %s OR email LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term, search_term])
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)
        
        if role_filter:
            query += " AND user_type = %s"
            params.append(role_filter)
        
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting users: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_user_by_id(user_id):
    conn = db.get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_tb WHERE user_id = %s", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def update_user_data(user_id, form_data):
    conn = db.get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_tb SET 
            firstname = %s, middlename = %s, lastname = %s,
            email = %s, mobile_number = %s, address = %s,
            user_type = %s, status = %s
            WHERE user_id = %s
        """, (
            form_data.get('firstname'), form_data.get('middlename'), form_data.get('lastname'),
            form_data.get('email'), form_data.get('mobile_number'), form_data.get('address'),
            form_data.get('user_type'), form_data.get('status'), user_id
        ))
        conn.commit()
    except Exception as e:
        print(f"Error updating user: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def toggle_user_status_db(user_id):
    conn = db.get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_tb SET status = CASE 
                WHEN status = 'active' THEN 'disabled'
                WHEN status = 'disabled' THEN 'active'
                ELSE 'active'
            END WHERE user_id = %s
        """, (user_id,))
        conn.commit()
    except Exception as e:
        print(f"Error toggling user status: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_all_blog_posts():
    conn = db.get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT bp.*, u.firstname, u.lastname 
            FROM blog_posts bp 
            LEFT JOIN user_tb u ON bp.author_id = u.user_id 
            ORDER BY bp.created_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting blog posts: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def toggle_blog_post_status(post_id):
    conn = db.get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE blog_posts SET status = CASE 
                WHEN status = 'draft' THEN 'published'
                WHEN status = 'published' THEN 'draft'
                ELSE 'draft'
            END WHERE id = %s
        """, (post_id,))
        conn.commit()
    except Exception as e:
        print(f"Error toggling post status: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_all_blog_comments():
    conn = db.get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT bc.*, u.firstname, u.lastname, bp.title as post_title
            FROM blog_comments bc 
            JOIN user_tb u ON bc.user_id = u.user_id 
            JOIN blog_posts bp ON bc.post_id = bp.id 
            ORDER BY bc.created_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting blog comments: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def moderate_blog_comment(comment_id, action):
    conn = db.get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE blog_comments SET status = %s WHERE id = %s", (action, comment_id))
        conn.commit()
    except Exception as e:
        print(f"Error moderating comment: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_all_games():
    conn = db.get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM games ORDER BY game_name")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting games: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def toggle_game_status(game_id):
    conn = db.get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE games SET is_active = NOT is_active WHERE id = %s", (game_id,))
        conn.commit()
    except Exception as e:
        print(f"Error toggling game status: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_game_access_list():
    conn = db.get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ga.*, u.firstname, u.lastname, g.game_name
            FROM game_access ga 
            JOIN user_tb u ON ga.user_id = u.user_id 
            JOIN games g ON ga.game_code = g.game_code 
            ORDER BY u.lastname, u.firstname
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting game access list: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def toggle_game_access_db(user_id, game_code):
    conn = db.get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO game_access (user_id, game_code, access_granted, created_at)
            VALUES (%s, %s, TRUE, NOW())
            ON DUPLICATE KEY UPDATE 
            access_granted = NOT access_granted,
            updated_at = NOW()
        """, (user_id, game_code))
        conn.commit()
    except Exception as e:
        print(f"Error toggling game access: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_system_settings():
    conn = db.get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM system_settings ORDER BY setting_key")
        settings = cursor.fetchall()
        return {s['setting_key']: s['setting_value'] for s in settings}
    except Exception as e:
        print(f"Error getting system settings: {e}")
        return {}
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def update_system_settings(form_data):
    conn = db.get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        for key, value in form_data.items():
            cursor.execute("""
                INSERT INTO system_settings (setting_key, setting_value) 
                VALUES (%s, %s) 
                ON DUPLICATE KEY UPDATE setting_value = %s
            """, (key, value, value))
        conn.commit()
    except Exception as e:
        print(f"Error updating system settings: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_activity_logs():
    conn = db.get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT al.*, u.firstname, u.lastname 
            FROM activity_logs al 
            LEFT JOIN user_tb u ON al.user_id = u.user_id 
            ORDER BY al.created_at DESC 
            LIMIT 100
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting activity logs: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_otp_list():
    conn = db.get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.*, u.firstname, u.lastname 
            FROM otp_tb o 
            LEFT JOIN user_tb u ON o.user_id = u.user_id 
            ORDER BY o.created_at DESC 
            LIMIT 50
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting OTP list: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_analytics_data():
    conn = db.get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # User registration stats (last 30 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM user_tb 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        user_registrations = cursor.fetchall()
        
        # Game usage stats
        cursor.execute("""
            SELECT g.game_name, COUNT(ga.id) as access_count
            FROM games g
            LEFT JOIN game_access ga ON g.game_code = ga.game_code AND ga.access_granted = TRUE
            GROUP BY g.game_name
            ORDER BY access_count DESC
        """)
        game_usage = cursor.fetchall()
        
        # Blog engagement
        cursor.execute("""
            SELECT bp.title, bp.view_count, COUNT(bc.id) as comment_count
            FROM blog_posts bp
            LEFT JOIN blog_comments bc ON bp.id = bc.post_id AND bc.status = 'approved'
            GROUP BY bp.id
            ORDER BY bp.view_count DESC
            LIMIT 10
        """)
        blog_engagement = cursor.fetchall()
        
        return {
            'user_registrations': user_registrations,
            'game_usage': game_usage,
            'blog_engagement': blog_engagement
        }
    except Exception as e:
        print(f"Error getting analytics data: {e}")
        return {}
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_blog_post_db(title, content, author_id, status, tags, featured_image):
    conn = db.get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO blog_posts (title, content, author_id, status, tags, featured_image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, content, author_id, status, tags, featured_image))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating blog post: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_security_data():
    conn = db.get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Recent login attempts
        cursor.execute("""
            SELECT action, COUNT(*) as count
            FROM activity_logs 
            WHERE action IN ('login_success', 'login_failed')
                AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY action
        """)
        login_attempts = cursor.fetchall()
        
        # Active sessions (simplified - in production you'd track actual sessions)
        cursor.execute("""
            SELECT user_id, COUNT(*) as activity_count
            FROM activity_logs 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
            GROUP BY user_id
        """)
        active_sessions = cursor.fetchall()
        
        # User activity tracking
        cursor.execute("""
            SELECT al.user_id, u.firstname, u.lastname, COUNT(*) as total_actions,
                   MAX(al.created_at) as last_activity
            FROM activity_logs al
            JOIN user_tb u ON al.user_id = u.user_id
            WHERE al.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY al.user_id
            ORDER BY total_actions DESC
            LIMIT 20
        """)
        user_activity = cursor.fetchall()
        
        return {
            'login_attempts': login_attempts,
            'active_sessions': active_sessions,
            'user_activity': user_activity
        }
    except Exception as e:
        print(f"Error getting security data: {e}")
        return {}
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
