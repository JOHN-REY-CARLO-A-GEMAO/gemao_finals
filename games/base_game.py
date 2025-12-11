"""
Base Game Class for Naruto-themed Tkinter Games
Demonstrates OOP principles: Inheritance, Polymorphism, Abstraction, Encapsulation
"""

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import messagebox
import random
import time

class BaseGame(ABC):
    """Abstract base class for all Naruto games"""
    
    def __init__(self, title="Naruto Game", width=800, height=600):
        # Encapsulation: Private attributes
        self._title = title
        self._width = width
        self._height = height
        self._score = 0
        self._is_running = False
        self._start_time = None
        
        # Initialize tkinter window
        self.root = tk.Tk()
        self.root.title(self._title)
        self.root.geometry(f"{self._width}x{self._height}")
        self.root.resizable(False, False)
        
        # Game state
        self.game_active = False
        self.high_score = self._load_high_score()
        
        # UI Elements
        self.score_label = None
        self.high_score_label = None
        self.time_label = None
        
    @abstractmethod
    def setup_ui(self):
        """Abstract method to setup game-specific UI"""
        pass
    
    @abstractmethod
    def start_game(self):
        """Abstract method to start the game (polymorphic)"""
        pass
    
    @abstractmethod
    def game_loop(self):
        """Abstract method for main game loop"""
        pass
    
    def _load_high_score(self):
        """Load high score from file (encapsulated method)"""
        try:
            with open(f"{self._title.replace(' ', '_')}_highscore.txt", 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def _save_high_score(self):
        """Save high score to file (encapsulated method)"""
        try:
            with open(f"{self._title.replace(' ', '_')}_highscore.txt", 'w') as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def update_score(self, points):
        """Update player score"""
        self._score += points
        if self.score_label:
            self.score_label.config(text=f"Score: {self._score}")
        
        # Check and update high score
        if self._score > self.high_score:
            self.high_score = self._score
            if self.high_score_label:
                self.high_score_label.config(text=f"High Score: {self.high_score}")
            self._save_high_score()
    
    def reset_score(self):
        """Reset score to zero"""
        self._score = 0
        if self.score_label:
            self.score_label.config(text=f"Score: {self._score}")
    
    def create_header(self):
        """Create common header UI elements"""
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text=self._title, 
                              font=('Arial', 18, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Score displays
        score_frame = tk.Frame(header_frame, bg='#2c3e50')
        score_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.score_label = tk.Label(score_frame, text=f"Score: {self._score}", 
                                   font=('Arial', 12), fg='white', bg='#2c3e50')
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        self.high_score_label = tk.Label(score_frame, text=f"High Score: {self.high_score}", 
                                        font=('Arial', 12), fg='#f39c12', bg='#2c3e50')
        self.high_score_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = tk.Label(score_frame, text="Time: 0s", 
                                  font=('Arial', 12), fg='white', bg='#2c3e50')
        self.time_label.pack(side=tk.LEFT, padx=10)
    
    def create_footer(self):
        """Create common footer UI elements"""
        footer_frame = tk.Frame(self.root, bg='#34495e', height=50)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        footer_frame.pack_propagate(False)
        
        # Control buttons
        tk.Button(footer_frame, text="Start Game", command=self.start_game,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Button(footer_frame, text="Reset", command=self.reset_game,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Button(footer_frame, text="Quit", command=self.quit_game,
                 bg='#95a5a6', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=10, pady=10)
    
    def update_timer(self):
        """Update game timer"""
        if self.game_active and self._start_time:
            elapsed = int(time.time() - self._start_time)
            if self.time_label:
                self.time_label.config(text=f"Time: {elapsed}s")
            self.root.after(1000, self.update_timer)
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.game_active = False
        self.reset_score()
        self._start_time = None
        if self.time_label:
            self.time_label.config(text="Time: 0s")
        self.setup_ui()
    
    def quit_game(self):
        """Quit the game"""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.quit()
            self.root.destroy()
    
    def show_game_over(self, message):
        """Show game over message"""
        self.game_active = False
        messagebox.showinfo("Game Over", f"{message}\nFinal Score: {self._score}")
    
    def run(self):
        """Main method to run the game (polymorphic entry point)"""
        self.create_header()
        self.setup_ui()
        self.create_footer()
        self.root.mainloop()

# Game Configuration Constants
GAME_CONFIG = {
    'colors': {
        'primary': '#e74c3c',
        'secondary': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'dark': '#2c3e50',
        'light': '#ecf0f1'
    },
    'fonts': {
        'title': ('Arial', 24, 'bold'),
        'subtitle': ('Arial', 18, 'bold'),
        'normal': ('Arial', 12),
        'small': ('Arial', 10)
    },
    'naruto_themes': {
        'characters': ['Naruto', 'Sasuke', 'Sakura', 'Kakashi', 'Rock Lee', 'Hinata', 'Shikamaru', 'Gaara'],
        'jutsus': ['Rasengan', 'Chidori', 'Shadow Clone', 'Fireball', 'Sharingan', 'Byakugan'],
        'villages': ['Leaf', 'Sand', 'Mist', 'Cloud', 'Stone'],
        'ranks': ['Genin', 'Chunin', 'Jonin', 'ANBU', 'Kage']
    }
}
