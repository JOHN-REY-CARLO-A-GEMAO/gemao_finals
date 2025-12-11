import tkinter as tk
from tkinter import messagebox
import random
import time
from tkinter_base_game import BaseGame as TkinterBaseGame

class TaijutsuComboGame(TkinterBaseGame):
    def __init__(self, master=None):
        super().__init__("Taijutsu Combo Training", width=500, height=400)
        self.moves = ["Punch", "Kick", "Block", "Elbow"]
        self.current_combo_sequence = []
        self.player_input_sequence = []
        self.combo_length = 3
        self.score = 0
        self.game_running_flag = False
        self.buttons = {}
        self.master = master

    def setup_ui(self):
        self.title_label = tk.Label(self.root, text="Taijutsu Combo Training!", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=("Arial", 14))
        self.score_label.pack(pady=5)

        self.combo_display_label = tk.Label(self.root, text="Memorize the combo!", font=("Arial", 12), wraplength=450)
        self.combo_display_label.pack(pady=10)

        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=10)

        for move in self.moves:
            button = tk.Button(self.input_frame, text=move, width=10, height=2,
                               command=lambda m=move: self._on_move_click(m), state=tk.DISABLED)
            button.pack(side=tk.LEFT, padx=5)
            self.buttons[move] = button

        self.start_button = tk.Button(self.root, text="Start Training", command=self._start_game, font=("Arial", 12))
        self.start_button.pack(pady=10)

    def _start_game(self):
        self.score = 0
        self.combo_length = 3
        self.score_label.config(text=f"Score: {self.score}")
        self.start_button.config(state=tk.DISABLED)
        self.game_running_flag = True
        self._next_combo_round()

    def _next_combo_round(self):
        if not self.game_running_flag:
            return

        self.player_input_sequence = []
        self.current_combo_sequence = self._generate_combo()
        self.combo_display_label.config(text="Memorize this combo:")

        for btn in self.buttons.values():
            btn.config(state=tk.DISABLED) # Disable input during display

        self.root.after(500, self._display_combo_sequence, 0) # Start displaying after a short delay

    def _generate_combo(self):
        return [random.choice(self.moves) for _ in range(self.combo_length)]

    def _display_combo_sequence(self, index):
        if index < len(self.current_combo_sequence):
            move = self.current_combo_sequence[index]
            self.combo_display_label.config(text=f"Displaying: {move}")
            # Simulate a quick highlight for the move (optional)
            if move in self.buttons:
                self.buttons[move].config(bg="yellow")
                self.root.update_idletasks()
                self.root.after(300, lambda: self.buttons[move].config(bg="SystemButtonFace"))
            self.root.after(800, self._display_combo_sequence, index + 1)
        else:
            self.combo_display_label.config(text="Now, perform the combo!")
            for btn in self.buttons.values():
                btn.config(state=tk.NORMAL) # Enable input after display

    def _on_move_click(self, move):
        if not self.game_running_flag:
            return

        self.player_input_sequence.append(move)
        self.combo_display_label.config(text=f"Your input: {' - '.join(self.player_input_sequence)}")

        if len(self.player_input_sequence) == len(self.current_combo_sequence):
            self.root.after(500, self._check_combo)

    def _check_combo(self):
        for btn in self.buttons.values():
            btn.config(state=tk.DISABLED) # Disable input during check

        if self.player_input_sequence == self.current_combo_sequence:
            self.score += 1
            self.combo_length += 1 # Increase combo length for next round
            self.score_label.config(text=f"Score: {self.score}")
            messagebox.showinfo("Correct!", "Excellent! Combo mastered!")
            self.root.after(1000, self._next_combo_round)
        else:
            messagebox.showerror("Combo Failed!", f"Incorrect combo. Game Over!\nYour final score: {self.score}\nThe correct combo was: {' - '.join(self.current_combo_sequence)}")
            self._end_game()

    def _end_game(self):
        self.game_running_flag = False
        self.start_button.config(text="Restart Training", state=tk.NORMAL)
        self.combo_display_label.config(text="Training complete!")


if __name__ == "__main__":
    game = TaijutsuComboGame()
    game.run()