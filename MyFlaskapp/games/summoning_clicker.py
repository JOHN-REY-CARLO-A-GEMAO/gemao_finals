import tkinter as tk
from tkinter import messagebox
from tkinter_base_game import BaseGame as TkinterBaseGame

class SummoningClickerGame(TkinterBaseGame):
    def __init__(self, master=None):
        super().__init__("Summoning Clicker", width=400, height=300)
        self.clicks = 0
        self.summoning_power = 0
        self.summon_cost = 100
        self.game_running_flag = False
        self.master = master # Store master if this game is part of a larger app

    def setup_ui(self):
        self.title_label = tk.Label(self.root, text="Summoning Clicker!", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        self.power_label = tk.Label(self.root, text=f"Summoning Power: {self.summoning_power}", font=("Arial", 14))
        self.power_label.pack(pady=5)

        self.cost_label = tk.Label(self.root, text=f"Next Summon Cost: {self.summon_cost}", font=("Arial", 12))
        self.cost_label.pack(pady=5)

        self.click_button = tk.Button(self.root, text="Gather Power (Click!)", command=self._gain_power,
                                      font=("Arial", 14), width=20, height=2, state=tk.DISABLED)
        self.click_button.pack(pady=10)

        self.summon_button = tk.Button(self.root, text="Summon Creature", command=self._summon_creature,
                                       font=("Arial", 14), width=20, height=2, state=tk.DISABLED)
        self.summon_button.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Game", command=self._start_game, font=("Arial", 12))
        self.start_button.pack(pady=5)

    def _start_game(self):
        self.clicks = 0
        self.summoning_power = 0
        self.summon_cost = 100
        self.power_label.config(text=f"Summoning Power: {self.summoning_power}")
        self.cost_label.config(text=f"Next Summon Cost: {self.summon_cost}")
        self.start_button.config(state=tk.DISABLED)
        self.click_button.config(state=tk.NORMAL)
        self.summon_button.config(state=tk.NORMAL)
        self.game_running_flag = True
        messagebox.showinfo("Game Started", "Start clicking to gather power and summon creatures!")

    def _gain_power(self):
        if self.game_running_flag:
            self.clicks += 1
            self.summoning_power += 10 # Gain 10 power per click
            self.power_label.config(text=f"Summoning Power: {self.summoning_power}")
            self._update_button_states()

    def _summon_creature(self):
        if self.game_running_flag:
            if self.summoning_power >= self.summon_cost:
                self.summoning_power -= self.summon_cost
                messagebox.showinfo("Summon Successful!", "You successfully summoned a creature!")
                self.summon_cost *= 2 # Increase cost for next summon
                self.power_label.config(text=f"Summoning Power: {self.summoning_power}")
                self.cost_label.config(text=f"Next Summon Cost: {self.summon_cost}")
                self._update_button_states()
            else:
                messagebox.showwarning("Not Enough Power", f"You need {self.summon_cost - self.summoning_power} more power to summon.")
    
    def _update_button_states(self):
        if self.summoning_power >= self.summon_cost:
            self.summon_button.config(state=tk.NORMAL)
        else:
            self.summon_button.config(state=tk.NORMAL) # Always active, just warn if not enough power

    def _end_game(self):
        self.game_running_flag = False
        self.click_button.config(state=tk.DISABLED)
        self.summon_button.config(state=tk.DISABLED)
        self.start_button.config(text="Play Again", state=tk.NORMAL)
        messagebox.showinfo("Game Over", f"You ended the game with {self.summoning_power} power and {self.clicks} clicks.")


if __name__ == "__main__":
    game = SummoningClickerGame()
    game.run()