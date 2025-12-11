from tkinter_base_game import BaseGame as TkinterBaseGame
import tkinter as tk
from tkinter import messagebox

class BaseNarutoGame(TkinterBaseGame):
    def __init__(self, title="Naruto Game", width=800, height=600):
        super().__init__(title, width, height)
        self.score = 0
        self.lives = 3
        self.level = 1
        self.colors = {
            'primary': '#FF4500',  # Orange-red
            'secondary': '#4682B4', # Steel blue
            'accent': '#FFD700',  # Gold
            'background': '#1a1a2e', # Dark blue-purple
            'text': '#E0E0E0'    # Light grey
        }
        self.setup_common_ui()

    def setup_common_ui(self):
        # Common UI elements for Naruto themed games
        self.header_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.header_frame.pack(fill=tk.X, pady=5)

        self.score_label = tk.Label(self.header_frame, text=f"Score: {self.score}", 
                                     fg=self.colors['text'], bg=self.colors['background'], font=('Arial', 12, 'bold'))
        self.score_label.pack(side=tk.LEFT, padx=10)

        self.lives_label = tk.Label(self.header_frame, text=f"Lives: {self.lives}",
                                     fg=self.colors['text'], bg=self.colors['background'], font=('Arial', 12, 'bold'))
        self.lives_label.pack(side=tk.RIGHT, padx=10)
        
        self.level_label = tk.Label(self.header_frame, text=f"Level: {self.level}",
                                     fg=self.colors['text'], bg=self.colors['background'], font=('Arial', 12, 'bold'))
        self.level_label.pack(side=tk.RIGHT, padx=10)

        self.game_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.game_frame.pack(fill=tk.BOTH, expand=True)

    def update_score(self, points):
        self.score += points
        self.score_label.config(text=f"Score: {self.score}")

    def update_lives(self, change):
        self.lives += change
        self.lives_label.config(text=f"Lives: {self.lives}")
        if self.lives <= 0:
            self.game_over_screen()

    def update_level(self):
        self.level += 1
        self.level_label.config(text=f"Level: {self.level}")

    def game_over_screen(self):
        messagebox.showinfo("Game Over", f"Your final score: {self.score}")
        self.root.destroy() # Close the game window

    def show_naruto_message(self, title, message):
        messagebox.showinfo(title, message)
        
    @property
    def is_running(self):
        return self.game_running

    @is_running.setter
    def is_running(self, value):
        self.game_running = value