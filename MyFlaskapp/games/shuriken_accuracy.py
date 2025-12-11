import tkinter as tk
from tkinter import messagebox
import random
import time
from tkinter_base_game import BaseGame as TkinterBaseGame

class ShurikenAccuracyGame(TkinterBaseGame):
    def __init__(self, master=None):
        super().__init__("Shuriken Accuracy Training", width=400, height=350)
        self.score = 0
        self.total_throws = 5 # Reduced for quicker gameplay in GUI
        self.throws_made = 0
        self.target_time = 0
        self.throw_start_time = 0
        self.game_running_flag = False
        self.master = master # Store master if this game is part of a larger app

    def setup_ui(self):
        self.title_label = tk.Label(self.root, text="Shuriken Accuracy Training!", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        self.instruction_label = tk.Label(self.root, text=f"You have {self.total_throws} shurikens. Click 'THROW!' at the target time.", font=("Arial", 10))
        self.instruction_label.pack(pady=5)

        self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=("Arial", 12))
        self.score_label.pack(pady=5)

        self.round_label = tk.Label(self.root, text=f"Throw: {self.throws_made}/{self.total_throws}", font=("Arial", 12))
        self.round_label.pack(pady=5)

        self.target_time_label = tk.Label(self.root, text="Target Time: ---", font=("Arial", 12))
        self.target_time_label.pack(pady=5)

        self.message_label = tk.Label(self.root, text="", font=("Arial", 10))
        self.message_label.pack(pady=5)

        self.throw_button = tk.Button(self.root, text="THROW!", command=self._on_throw_click, state=tk.DISABLED,
                                      font=("Arial", 14), width=10, height=2)
        self.throw_button.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Training", command=self._start_game, font=("Arial", 12))
        self.start_button.pack(pady=5)

    def _start_game(self):
        self.score = 0
        self.throws_made = 0
        self.score_label.config(text=f"Score: {self.score}")
        self.round_label.config(text=f"Throw: {self.throws_made}/{self.total_throws}")
        self.start_button.config(state=tk.DISABLED)
        self.game_running_flag = True
        self._next_throw()

    def _next_throw(self):
        if self.throws_made < self.total_throws and self.game_running_flag:
            self.throws_made += 1
            self.round_label.config(text=f"Throw: {self.throws_made}/{self.total_throws}")
            self.target_time = random.uniform(1.0, 3.0)
            self.target_time_label.config(text=f"Target Time: {self.target_time:.2f} seconds!")
            self.message_label.config(text="Get Ready...")
            self.throw_button.config(state=tk.DISABLED, bg="SystemButtonFace")
            
            # Simulate a variable delay before the "THROW!" button becomes active
            delay_before_active = random.randint(1000, 3000) # 1 to 3 seconds
            self.root.after(delay_before_active, self._activate_throw_button)
        else:
            self._end_game()

    def _activate_throw_button(self):
        if self.game_running_flag:
            self.message_label.config(text="NOW!")
            self.throw_button.config(state=tk.NORMAL, bg="green")
            self.throw_start_time = time.time()

    def _on_throw_click(self):
        if self.game_running_flag and self.throw_button['state'] == tk.NORMAL:
            throw_end_time = time.time()
            self.throw_button.config(state=tk.DISABLED, bg="SystemButtonFace") # Disable after click

            throw_duration = throw_end_time - self.throw_start_time
            accuracy = abs(self.target_time - throw_duration)

            points = 0
            message = ""
            if accuracy < 0.1:
                points = 10
                message = "BULLSEYE!"
            elif accuracy < 0.3:
                points = 7
                message = "Good throw!"
            elif accuracy < 0.6:
                points = 4
                message = "Decent throw."
            else:
                points = 1
                message = "Needs practice."
            
            self.score += points
            self.score_label.config(text=f"Score: {self.score}")
            self.message_label.config(text=f"You threw in {throw_duration:.2f}s. Deviation: {accuracy:.2f}s. {message} (+{points} pts)")

            self.root.after(2000, self._next_throw) # Delay before next throw
        elif not self.game_running_flag:
            messagebox.showinfo("Game Over", "Please start training to throw shurikens.")

    def _end_game(self):
        self.game_running_flag = False
        messagebox.showinfo("Training Complete", f"Your final accuracy score: {self.score}!")
        self.start_button.config(text="Restart Training", state=tk.NORMAL)
        self.target_time_label.config(text="Target Time: ---")
        self.message_label.config(text="")


if __name__ == "__main__":
    game = ShurikenAccuracyGame()
    game.run()