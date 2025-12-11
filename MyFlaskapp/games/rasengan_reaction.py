import tkinter as tk
from tkinter import messagebox
import random
import time
from tkinter_base_game import BaseGame as TkinterBaseGame

class RasenganReactionGame(TkinterBaseGame):
    def __init__(self, master=None):
        super().__init__("Rasengan Reaction", width=400, height=300)
        self.player_score = 0
        self.rounds_played = 0
        self.total_rounds = 5
        self.reaction_start_time = 0
        self.game_running_flag = False
        self.master = master # Store master if this game is part of a larger app

    def setup_ui(self):
        self.title_label = tk.Label(self.root, text="Rasengan Reaction!", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        self.instruction_label = tk.Label(self.root, text="Click 'ATTACK!' as fast as you can when it appears.", font=("Arial", 12))
        self.instruction_label.pack(pady=5)

        self.score_label = tk.Label(self.root, text=f"Score: {self.player_score}", font=("Arial", 14))
        self.score_label.pack(pady=5)

        self.message_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.message_label.pack(pady=5)

        self.attack_button = tk.Button(self.root, text="Prepare...", command=self._on_attack_click, state=tk.DISABLED,
                                       font=("Arial", 16), width=15, height=2)
        self.attack_button.pack(pady=20)

        self.start_button = tk.Button(self.root, text="Start Game", command=self._start_game, font=("Arial", 12))
        self.start_button.pack(pady=10)

    def _start_game(self):
        self.player_score = 0
        self.rounds_played = 0
        self.score_label.config(text=f"Score: {self.player_score}")
        self.start_button.config(state=tk.DISABLED)
        self.game_running_flag = True
        self._next_round()

    def _next_round(self):
        if self.rounds_played < self.total_rounds and self.game_running_flag:
            self.rounds_played += 1
            self.message_label.config(text=f"Round {self.rounds_played}/{self.total_rounds}. Get Ready!")
            self.attack_button.config(text="Prepare...", state=tk.DISABLED)
            delay = random.randint(1, 4) * 1000 # Random delay between 1 and 4 seconds in ms
            self.root.after(delay, self._show_attack_button)
        else:
            self._end_game()

    def _show_attack_button(self):
        if self.game_running_flag:
            self.message_label.config(text="ATTACK!")
            self.attack_button.config(text="ATTACK!", state=tk.NORMAL, bg="red", fg="white")
            self.reaction_start_time = time.time()
            self.root.bind("<Return>", self._on_enter_press) # Bind Enter key for quick reaction

    def _on_attack_click(self):
        if self.game_running_flag and self.attack_button['state'] == tk.NORMAL:
            self.root.unbind("<Return>") # Unbind Enter key
            end_time = time.time()
            reaction_time = end_time - self.reaction_start_time
            self.message_label.config(text=f"Your reaction time: {reaction_time:.3f} seconds")
            self.attack_button.config(text="Waiting...", state=tk.DISABLED, bg="SystemButtonFace", fg="black")

            # Scoring: lower reaction time is better, max 10 points
            points = max(0, int(10 - (reaction_time * 2))) # Adjust multiplier as needed
            self.player_score += points
            self.score_label.config(text=f"Score: {self.player_score}")
            self.root.after(1500, self._next_round) # Delay before next round
        elif not self.game_running_flag:
            messagebox.showinfo("Game Over", "Please start a new game to play.")


    def _on_enter_press(self, event=None):
        self._on_attack_click()

    def _end_game(self):
        self.game_running_flag = False
        messagebox.showinfo("Game Over", f"Your final score: {self.player_score} points!")
        self.start_button.config(text="Play Again", state=tk.NORMAL)
        self.attack_button.config(state=tk.DISABLED, text="Prepare...", bg="SystemButtonFace", fg="black")
        self.message_label.config(text="")


if __name__ == "__main__":
    game = RasenganReactionGame()
    game.run()