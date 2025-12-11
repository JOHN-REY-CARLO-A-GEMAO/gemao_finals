import tkinter as tk
from tkinter import messagebox
import random
from tkinter_base_game import BaseGame as TkinterBaseGame

class GuessNinjaGame(TkinterBaseGame):
    def __init__(self, master=None):
        super().__init__("Guess the Ninja", width=500, height=350)
        self.ninjas = {
            "naruto": "The protagonist of the series, known for his spiky blonde hair and love for ramen.",
            "sasuke": "A member of the Uchiha clan, known for his Sharingan and rival to Naruto.",
            "sakura": "A kunoichi of Team 7, skilled in medical ninjutsu and super strength.",
            "kakashi": "The sensei of Team 7, known for his masked face and sharingan eye.",
            "itachi": "A powerful Uchiha who massacred his clan for the sake of the village.",
            "jiraiya": "The Pervy Sage, one of the Legendary Sannin, and Naruto's godfather.",
            "minato": "The Fourth Hokage, known as the Yellow Flash of Konoha, and Naruto's father.",
            "hinata": "A gentle kunoichi from the Hyuga clan, with a strong crush on Naruto."
        }
        self.current_ninja_names_for_round = []
        self.current_ninja_index = 0
        self.score = 0
        self.total_rounds = 5 # Number of ninjas to guess per game
        self.game_running_flag = False
        self.master = master

    def setup_ui(self):
        self.title_label = tk.Label(self.root, text="Guess the Ninja!", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=("Arial", 14))
        self.score_label.pack(pady=5)

        self.round_label = tk.Label(self.root, text="Round: 0/0", font=("Arial", 12))
        self.round_label.pack(pady=5)

        self.description_label = tk.Label(self.root, text="Press Start to begin!", font=("Arial", 12), wraplength=450)
        self.description_label.pack(pady=10)

        self.guess_entry = tk.Entry(self.root, width=30, font=("Arial", 12))
        self.guess_entry.pack(pady=5)
        self.guess_entry.bind("<Return>", self._check_guess_event) # Allow Enter to submit

        self.submit_button = tk.Button(self.root, text="Submit Guess", command=self._check_guess, state=tk.DISABLED,
                                       font=("Arial", 12))
        self.submit_button.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Game", command=self._start_game, font=("Arial", 12))
        self.start_button.pack(pady=5)

    def _start_game(self):
        self.score = 0
        self.current_ninja_index = 0
        self.current_ninja_names_for_round = random.sample(list(self.ninjas.keys()), 
                                                            min(self.total_rounds, len(self.ninjas)))
        self.score_label.config(text=f"Score: {self.score}")
        self.start_button.config(state=tk.DISABLED)
        self.guess_entry.config(state=tk.NORMAL)
        self.submit_button.config(state=tk.NORMAL)
        self.game_running_flag = True
        self._load_next_ninja()

    def _load_next_ninja(self):
        if self.current_ninja_index < len(self.current_ninja_names_for_round):
            ninja_name = self.current_ninja_names_for_round[self.current_ninja_index]
            description = self.ninjas[ninja_name]
            self.round_label.config(text=f"Round: {self.current_ninja_index + 1}/{len(self.current_ninja_names_for_round)}")
            self.description_label.config(text=f"Description: {description}")
            self.guess_entry.delete(0, tk.END) # Clear previous guess
            self.guess_entry.focus_set() # Set focus to entry widget
        else:
            self._end_game()

    def _check_guess_event(self, event=None):
        self._check_guess()

    def _check_guess(self):
        if not self.game_running_flag:
            return

        user_guess = self.guess_entry.get().strip().lower()
        correct_ninja = self.current_ninja_names_for_round[self.current_ninja_index]

        if user_guess == correct_ninja:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            messagebox.showinfo("Correct!", "You guessed correctly!")
        else:
            messagebox.showerror("Incorrect!", f"Wrong! The ninja was {correct_ninja.capitalize()}.")
        
        self.current_ninja_index += 1
        self.root.after(1000, self._load_next_ninja) # Load next ninja after a delay

    def _end_game(self):
        self.game_running_flag = False
        messagebox.showinfo("Game Over", f"Your final score: {self.score}/{len(self.current_ninja_names_for_round)}")
        self.start_button.config(text="Play Again", state=tk.NORMAL)
        self.guess_entry.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)
        self.description_label.config(text="Thanks for playing Guess the Ninja!")
        self.round_label.config(text="Round: 0/0")


if __name__ == "__main__":
    game = GuessNinjaGame()
    game.run()