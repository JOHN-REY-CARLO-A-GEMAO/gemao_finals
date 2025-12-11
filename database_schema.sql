-- Naruto Flask System - Complete Database Schema
-- This schema extends the existing user_tb with comprehensive functionality

USE gemao_db;

-- Enhanced user_tb table (restructure existing user_tb)
-- DROP TABLE IF EXISTS users;

-- User profiles extended information
DROP TABLE IF EXISTS profiles;
CREATE TABLE profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    birthday DATE,
    age INT GENERATED ALWAYS AS (TIMESTAMPDIFF(YEAR, birthday, CURDATE())) VIRTUAL,
    contact VARCHAR(20),
    email VARCHAR(100) NOT NULL,
    dream_job VARCHAR(100),
    bio TEXT,
    avatar_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_tb(user_id) ON DELETE CASCADE
);

-- OTP verification table
DROP TABLE IF EXISTS otp_tb;
CREATE TABLE otp_tb (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    otp_code VARCHAR(4) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 15 MINUTE),
    used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES user_tb(user_id) ON DELETE CASCADE,
    INDEX idx_otp_user (user_id),
    INDEX idx_otp_code (otp_code)
);

-- Games table
DROP TABLE IF EXISTS games;
CREATE TABLE games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_name VARCHAR(100) NOT NULL,
    game_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    game_type ENUM('memory', 'reaction', 'accuracy', 'balance', 'trivia', 'clicker', 'maze', 'combo', 'defense', 'guessing') NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    thumbnail_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_game_code (game_code),
    INDEX idx_game_type (game_type)
);

-- Game access control
DROP TABLE IF EXISTS game_access;
CREATE TABLE game_access (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    game_code VARCHAR(50) NOT NULL,
    access_granted BOOLEAN DEFAULT TRUE,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES user_tb(user_id) ON DELETE CASCADE,
    FOREIGN KEY (game_code) REFERENCES games(game_code) ON DELETE CASCADE,
    UNIQUE KEY unique_user_game (user_id, game_code)
);

-- Blog posts
DROP TABLE IF EXISTS blog_posts;
CREATE TABLE blog_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id VARCHAR(50) NOT NULL,
    status ENUM('draft', 'published') DEFAULT 'draft',
    featured_image VARCHAR(255),
    tags VARCHAR(255),
    view_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES user_tb(user_id) ON DELETE CASCADE,
    INDEX idx_author (author_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
);

-- Blog comments
DROP TABLE IF EXISTS blog_comments;
CREATE TABLE blog_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    comment TEXT NOT NULL,
    status ENUM('pending', 'approved') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES blog_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user_tb(user_id) ON DELETE CASCADE,
    INDEX idx_post (post_id),
    INDEX idx_user (user_id),
    INDEX idx_status (status)
);

-- Activity logs
DROP TABLE IF EXISTS activity_logs;
CREATE TABLE activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_tb(user_id) ON DELETE SET NULL,
    INDEX idx_user_activity (user_id),
    INDEX idx_action (action),
    INDEX idx_created (created_at)
);

-- System settings
DROP TABLE IF EXISTS system_settings;
CREATE TABLE system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_by VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES user_tb(user_id) ON DELETE SET NULL
);

-- Insert default admin user into user_tb
INSERT IGNORE INTO user_tb (user_id, firstname, lastname, username, password, email, user_type, status)
VALUES ('admin001', 'Admin', 'User', 'admin', 'admin123', 'admin@naruto-system.com', 'admin', 'active');

-- Insert Naruto games
INSERT INTO games (game_name, game_code, description, game_type, file_path) VALUES
('Shadow Clone Memory Match', 'shadow_clone', 'Match pairs of shadow clones in this memory game', 'memory', 'games/shadow_clone_memory.py'),
('Rasengan Reaction Test', 'rasengan_reaction', 'Test your reaction time with Rasengan charging', 'reaction', 'games/rasengan_reaction.py'),
('Shuriken Accuracy Throw', 'shuriken_throw', 'Throw shurikens at targets with precision', 'accuracy', 'games/shuriken_accuracy.py'),

('Ninja Trivia Challenge', 'ninja_trivia', 'Test your Naruto knowledge with trivia questions', 'trivia', 'games/ninja_trivia.py'),
('Summoning Beast Clicker', 'summoning_clicker', 'Click fast to summon powerful beasts', 'clicker', 'games/summoning_clicker.py'),
('Escape the Anbu Maze', 'anbu_maze', 'Navigate through the Anbu maze to escape', 'maze', 'games/anbu_maze.py'),
('Taijutsu Combo Builder', 'taijutsu_combo', 'Build powerful combos like Rock Lee', 'combo', 'games/taijutsu_combo.py'),
('Hokage Tower Defense', 'hokage_defense', 'Defend the Hokage tower from enemies', 'defense', 'games/hokage_defense.py'),
('Guess the Ninja', 'guess_ninja', 'Identify ninjas from their silhouettes', 'guessing', 'games/guess_ninja.py');

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('site_name', 'Ninja Academy System', 'Name of the system'),
('allow_registration', 'true', 'Allow public user registration'),
('otp_expiry_minutes', '15', 'OTP code expiry time in minutes'),
('max_login_attempts', '5', 'Maximum failed login attempts before lockout'),
('session_timeout', '30', 'Session timeout in minutes');

-- Grant all active users access to all games
INSERT INTO game_access (user_id, game_code, granted_by)
SELECT u.user_id, g.game_code, 'admin001'
FROM user_tb u, games g
WHERE u.status = 'active';

