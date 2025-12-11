from flask import render_template, redirect, url_for, flash, request, session, send_file
from . import games_bp
from MyFlaskapp.db import get_db_connection
from MyFlaskapp.utils import login_required, log_activity
from datetime import datetime
import os
import subprocess
import sys

@games_bp.route('/')
@login_required
def games_home():
    """Games listing page"""
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    games_list = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT g.*, ga.access_granted, ga.granted_at
                FROM games g
                LEFT JOIN game_access ga ON g.game_code = ga.game_code AND ga.user_id = %s
                WHERE g.is_active = TRUE
                ORDER BY g.game_name
            """, (user_id,))
            games_list = cursor.fetchall()
            
        except Exception as e:
            print(f"Error getting games: {e}")
        finally:
            conn.close()
    
    return render_template('games/index.html', games=games_list)

@games_bp.route('/my-games')
@login_required
def my_games():
    """User's accessible games"""
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    user_games = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT g.*, ga.granted_at
                FROM games g
                JOIN game_access ga ON g.game_code = ga.game_code
                WHERE ga.user_id = %s AND ga.access_granted = TRUE AND g.is_active = TRUE
                ORDER BY g.game_name
            """, (user_id,))
            user_games = cursor.fetchall()
            
        except Exception as e:
            print(f"Error getting user games: {e}")
        finally:
            conn.close()
    
    return render_template('games/my_games.html', games=user_games)

@games_bp.route('/play/<game_code>')
@login_required
def play_game(game_code):
    """Launch a specific game"""
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    game = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if user has access to this game
            cursor.execute("""
                SELECT g.*, ga.access_granted
                FROM games g
                LEFT JOIN game_access ga ON g.game_code = ga.game_code AND ga.user_id = %s
                WHERE g.game_code = %s AND g.is_active = TRUE
            """, (user_id, game_code))
            game = cursor.fetchone()
            
            if not game or not game.get('access_granted'):
                flash('Game not found or access denied', 'danger')
                return redirect(url_for('games.games_home'))
            
            # Log game launch
            log_activity(user_id, 'game_launched', f'Launched game: {game["game_name"]}', request.remote_addr)
            
            # Get the full path to the game file
            game_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'games', os.path.basename(game['file_path']))
            
            if os.path.exists(game_path):
                try:
                    # Launch the game in a new process
                    subprocess.Popen([sys.executable, game_path])
                    flash(f'{game["game_name"]} launched successfully!', 'success')
                except Exception as e:
                    print(f"Error launching game: {e}")
                    flash('Error launching game. Please try again.', 'danger')
            else:
                flash('Game file not found', 'danger')
            
        except Exception as e:
            print(f"Error checking game access: {e}")
            flash('Error accessing game', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('games.games_home'))

@games_bp.route('/leaderboard/<game_code>')
@login_required
def leaderboard(game_code):
    """Game leaderboard (placeholder for future implementation)"""
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    game = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM games WHERE game_code = %s", (game_code,))
            game = cursor.fetchone()
            
        except Exception as e:
            print(f"Error getting game for leaderboard: {e}")
        finally:
            conn.close()
    
    if not game:
        flash('Game not found', 'danger')
        return redirect(url_for('games.games_home'))
    
    # Placeholder leaderboard data
    leaderboard_data = [
        {'rank': 1, 'username': 'NarutoUzumaki', 'score': 9999, 'date': '2024-01-15'},
        {'rank': 2, 'username': 'SasukeUchiha', 'score': 8500, 'date': '2024-01-14'},
        {'rank': 3, 'username': 'SakuraHaruno', 'score': 7200, 'date': '2024-01-13'},
        {'rank': 4, 'username': 'KakashiHatake', 'score': 6800, 'date': '2024-01-12'},
        {'rank': 5, 'username': 'RockLee', 'score': 5500, 'date': '2024-01-11'},
    ]
    
    return render_template('games/leaderboard.html', game=game, leaderboard=leaderboard_data)

@games_bp.route('/achievements')
@login_required
def achievements():
    """User achievements page"""
    user_id = session.get('user_id')
    
    # Placeholder achievements data
    achievements_data = [
        {
            'id': 1,
            'name': 'Shadow Clone Master',
            'description': 'Complete Shadow Clone Memory Match with perfect score',
            'icon': '👥',
            'unlocked': True,
            'unlocked_date': '2024-01-10'
        },
        {
            'id': 2,
            'name': 'Rasengan Expert',
            'description': 'Achieve maximum reaction time in Rasengan Test',
            'icon': '⚡',
            'unlocked': True,
            'unlocked_date': '2024-01-08'
        },
        {
            'id': 3,
            'name': 'Shuriken Sharpshooter',
            'description': 'Hit 10 consecutive targets in Shuriken Throw',
            'icon': '🥷',
            'unlocked': False,
            'unlocked_date': None
        },
        {
            'id': 4,
            'name': 'Chakra Control Master',
            'description': 'Balance for 60 seconds in Chakra Control',
            'icon': '🧘',
            'unlocked': False,
            'unlocked_date': None
        },
        {
            'id': 5,
            'name': 'Ninja Trivia Champion',
            'description': 'Answer 50 trivia questions correctly',
            'icon': '📚',
            'unlocked': True,
            'unlocked_date': '2024-01-05'
        }
    ]
    
    # Calculate statistics
    total_achievements = len(achievements_data)
    unlocked_achievements = sum(1 for a in achievements_data if a['unlocked'])
    
    return render_template('games/achievements.html', 
                         achievements=achievements_data,
                         total_achievements=total_achievements,
                         unlocked_achievements=unlocked_achievements)

@games_bp.route('/stats')
@login_required
def stats():
    """Game statistics page"""
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    stats_data = {
        'games_played': 0,
        'total_playtime': 0,
        'favorite_game': None,
        'recent_activity': []
    }
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get user's accessible games
            cursor.execute("""
                SELECT COUNT(DISTINCT g.game_code) as games_played
                FROM games g
                JOIN game_access ga ON g.game_code = ga.game_code
                WHERE ga.user_id = %s AND ga.access_granted = TRUE AND g.is_active = TRUE
            """, (user_id,))
            result = cursor.fetchone()
            stats_data['games_played'] = result['games_played'] if result else 0
            
            # Placeholder for recent activity (would come from game_logs table in real implementation)
            stats_data['recent_activity'] = [
                {'game': 'Shadow Clone Memory Match', 'action': 'Played', 'time': '2 hours ago', 'score': 850},
                {'game': 'Rasengan Reaction Test', 'action': 'Played', 'time': '5 hours ago', 'score': 92},
                {'game': 'Ninja Trivia Challenge', 'action': 'Played', 'time': '1 day ago', 'score': 45},
            ]
            
        except Exception as e:
            print(f"Error getting game stats: {e}")
        finally:
            conn.close()
    
    return render_template('games/stats.html', stats=stats_data)
