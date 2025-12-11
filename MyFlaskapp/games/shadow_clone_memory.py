import tkinter as tk
from tkinter import messagebox
import random
import time
from tkinter_base_game import BaseGame as TkinterBaseGame

class ShadowCloneMemoryGame(TkinterBaseGame):
    def __init__(self, master=None):
        super().__init__("Shadow Clone Memory", width=500, height=400)
        self.sequence = []
        self.player_sequence_input = []
        self.player_score = 0
        self.sequence_length = 1
        self.game_active = False
        self.clone_options = ['clone1', 'clone2', 'clone3', 'clone4']
        self.buttons = {}
        self.master = master # Store master if this game is part of a larger app

    def setup_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        self.root.rowconfigure(4, weight=1)

        self.score_label = tk.Label(self.root, text=f"Score: {self.player_score}", font=("Arial", 14))
        self.score_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.message_label = tk.Label(self.root, text="Press Start to begin!", font=("Arial", 12))
        self.message_label.grid(row=1, column=0, columnspan=2, pady=10)

        for i, clone_name in enumerate(self.clone_options):
            button = tk.Button(self.root, text=clone_name.capitalize(), width=15, height=3,
                               command=lambda c=clone_name: self._on_clone_click(c), state=tk.DISABLED)
            self.buttons[clone_name] = button
            row = 2 + (i // 2)
            col = i % 2
            button.grid(row=row, column=col, padx=5, pady=5)

        self.start_button = tk.Button(self.root, text="Start Game", command=self._start_game_round, font=("Arial", 12))
        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

    def _on_clone_click(self, clone_name):
        if self.game_active:
            self.player_sequence_input.append(clone_name)
            self.message_label.config(text=f"You chose: {clone_name.capitalize()}")
            if len(self.player_sequence_input) == len(self.sequence):
                self.root.after(500, self._check_player_input)

    def _start_game_round(self):
        self.start_button.config(state=tk.DISABLED)
        self.game_active = False
        self.player_sequence_input = []
        self._generate_sequence(self.sequence_length)
        self.message_label.config(text="Memorize the sequence!")
        for button in self.buttons.values():
            button.config(state=tk.DISABLED)
        self.root.after(1000, self._display_sequence_gui, 0) # Start displaying after a delay

    def _generate_sequence(self, length):
        self.sequence = [random.choice(self.clone_options) for _ in range(length)]

    def _display_sequence_gui(self, index):
        if index < len(self.sequence):
            clone_to_display = self.sequence[index]
            self.message_label.config(text=f"Displaying: {clone_to_display.capitalize()}")
            # Simulate clone display by highlighting a button (optional)
            self.buttons[clone_to_display].config(bg="yellow")
            self.root.update_idletasks() # Force update
            self.root.after(500, lambda: self.buttons[clone_to_display].config(bg="SystemButtonFace"))
            self.root.after(1000, self._display_sequence_gui, index + 1)
        else:
            self.message_label.config(text="Now, repeat the sequence!")
            for button in self.buttons.values():
                button.config(state=tk.NORMAL)
            self.game_active = True

    def _check_player_input(self):
        self.game_active = False
        for button in self.buttons.values():
            button.config(state=tk.DISABLED)

        if self.player_sequence_input == self.sequence:
            self.player_score += 1
            self.sequence_length += 1
            self.score_label.config(text=f"Score: {self.player_score}")
            self.message_label.config(text="Correct! Next round...")
            self.root.after(1500, self._start_game_round)
        else:
            messagebox.showinfo("Game Over", f"Incorrect sequence. Game Over!\nYour final score: {self.player_score}")
            self.start_button.config(text="Play Again", state=tk.NORMAL)
            self.player_score = 0
            self.sequence_length = 1
            self.score_label.config(text=f"Score: {self.player_score}")
            self.message_label.config(text="Press Play Again to start a new game!")


if __name__ == "__main__":
    game = ShadowCloneMemoryGame()
    game.run()