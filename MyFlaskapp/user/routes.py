from flask import render_template, redirect, url_for, flash, request, session, current_app
from werkzeug.utils import secure_filename
from . import user_bp
from MyFlaskapp.db import get_db_connection
from MyFlaskapp.utils import login_required, log_activity
from datetime import datetime
import os


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with profile and games access"""
    user_id = session.get('user_id')
    user_info = session.get('user_info', {})
    
    conn = get_db_connection()
    dashboard_data = {
        'user_games': [],
        'recent_posts': [],
        'user_stats': {}
    }
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get user's accessible games
            cursor.execute("""
                SELECT g.* FROM games g
                JOIN game_access ga ON g.game_code = ga.game_code
                WHERE ga.user_id = %s AND ga.access_granted = TRUE AND g.is_active = TRUE
                ORDER BY g.game_name
            """, (user_id,))
            dashboard_data['user_games'] = cursor.fetchall()
            
            # Get recent blog posts
            cursor.execute("""
                SELECT bp.*, u.firstname, u.lastname 
                FROM blog_posts bp 
                LEFT JOIN user_tb u ON bp.author_id = u.user_id 
                WHERE bp.status = 'published'
                ORDER BY bp.created_at DESC 
                LIMIT 5
            """)
            dashboard_data['recent_posts'] = cursor.fetchall()
            
            # Get user statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT ga.game_code) as games_played,
                    (SELECT COUNT(*) FROM blog_posts WHERE author_id = %s) as posts_written
                FROM game_access ga
                WHERE ga.user_id = %s
            """, (user_id, user_id))
            dashboard_data['user_stats'] = cursor.fetchone() or {}
            
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
        finally:
            conn.close()
    
    return render_template('user/dashboard.html', 
                         user_info=user_info, 
                         dashboard_data=dashboard_data)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    user_data = {}
    profile_data = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get user data
            cursor.execute("SELECT * FROM user_tb WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone() or {}
            
            # Get profile data
            cursor.execute("SELECT * FROM profiles WHERE user_id = %s", (user_id,))
            profile_data = cursor.fetchone() or {}
            
            if request.method == 'POST':
                # Update profile
                firstname = request.form.get('firstname')
                lastname = request.form.get('lastname')
                middlename = request.form.get('middlename', '')
                birthdate = request.form.get('birthdate')
                address = request.form.get('address', '')
                mobile_number = request.form.get('mobile_number', '')
                dream_job = request.form.get('dream_job', '')
                bio = request.form.get('bio', '')
                
                # Update users table
                cursor.execute("""
                    UPDATE user_tb SET 
                        firstname = %s, lastname = %s, middlename = %s,
                        birthdate = %s, address = %s, mobile_number = %s
                    WHERE user_id = %s
                """, (firstname, lastname, middlename, birthdate, address, mobile_number, user_id))
                
                # Update or insert profile
                cursor.execute("""
                    INSERT INTO profiles (user_id, first_name, middle_name, last_name, birthday, contact, email, dream_job, bio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        first_name = %s, middle_name = %s, last_name = %s, birthday = %s,
                        contact = %s, email = %s, dream_job = %s, bio = %s
                """, (user_id, firstname, middlename, lastname, birthdate, mobile_number, user_data.get('email'), dream_job, bio,
                       firstname, middlename, lastname, birthdate, mobile_number, user_data.get('email'), dream_job, bio))
                
                conn.commit()
                log_activity(user_id, 'profile_updated', 'Updated profile information', request.remote_addr)
                flash('Profile updated successfully', 'success')
                
                # Refresh data
                cursor.execute("SELECT * FROM user_tb WHERE user_id = %s", (user_id,))
                user_data = cursor.fetchone()
                cursor.execute("SELECT * FROM profiles WHERE user_id = %s", (user_id,))
                profile_data = cursor.fetchone()
                
                # Update session
                session['user_name'] = f"{user_data['firstname']} {user_data['lastname']}"
                session['user_info'] = user_data
                
        except Exception as e:
            print(f"Error updating profile: {e}")
            flash('Error updating profile', 'danger')
        finally:
            conn.close()
    
    return render_template('user/profile.html', user_data=user_data, profile_data=profile_data)

@user_bp.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload user avatar"""
    user_id = session.get('user_id')
    
    if 'avatar' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('user.profile'))
    
    file = request.files['avatar']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('user.profile'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}")
        
        # Create uploads directory if it doesn't exist
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Update database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                avatar_url = f"/static/uploads/avatars/{filename}"
                cursor.execute("UPDATE user_tb SET avatar_url = %s WHERE user_id = %s", (avatar_url, user_id))
                conn.commit()
                
                log_activity(user_id, 'avatar_uploaded', 'Uploaded new avatar', request.remote_addr)
                flash('Avatar uploaded successfully', 'success')
                
            except Exception as e:
                print(f"Error uploading avatar: {e}")
                flash('Error uploading avatar', 'danger')
            finally:
                conn.close()
    else:
        flash('Invalid file type. Please upload JPG, PNG, or GIF', 'danger')
    
    return redirect(url_for('user.profile'))

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
