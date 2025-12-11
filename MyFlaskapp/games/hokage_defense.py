import tkinter as tk
from tkinter import messagebox
import random
import time
from tkinter_base_game import BaseGame as TkinterBaseGame

class HokageDefenseGame(TkinterBaseGame):
    def __init__(self, master=None):
        super().__init__("Hokage Defense", width=600, height=500)
        self.village_health = 100
        self.current_wave = 0
        self.enemies_remaining = 0
        self.game_running_flag = False
        self.master = master
        self.enemy_spawn_interval = 1000 # milliseconds

    def setup_ui(self):
        self.title_label = tk.Label(self.root, text="Hokage Defense!", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)

        self.health_label = tk.Label(self.root, text=f"Village Health: {self.village_health}", font=("Arial", 14), fg="green")
        self.health_label.pack(pady=5)

        self.wave_label = tk.Label(self.root, text=f"Wave: {self.current_wave}", font=("Arial", 14))
        self.wave_label.pack(pady=5)

        self.enemies_label = tk.Label(self.root, text=f"Enemies Remaining: {self.enemies_remaining}", font=("Arial", 12))
        self.enemies_label.pack(pady=5)

        self.message_label = tk.Label(self.root, text="Press Start to defend the village!", font=("Arial", 12))
        self.message_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Defense", command=self._start_game, font=("Arial", 12))
        self.start_button.pack(pady=5)

    def _start_game(self):
        self.village_health = 100
        self.current_wave = 0
        self.enemies_remaining = 0
        self.health_label.config(text=f"Village Health: {self.village_health}", fg="green")
        self.wave_label.config(text=f"Wave: {self.current_wave}")
        self.enemies_label.config(text=f"Enemies Remaining: {self.enemies_remaining}")
        self.start_button.config(state=tk.DISABLED)
        self.game_running_flag = True
        self._next_wave()

    def _next_wave(self):
        if not self.game_running_flag:
            return

        self.current_wave += 1
        self.wave_label.config(text=f"Wave: {self.current_wave}")
        self.enemies_to_spawn_this_wave = self.current_wave * 2
        self.enemies_remaining = self.enemies_to_spawn_this_wave
        self.enemies_label.config(text=f"Enemies Remaining: {self.enemies_remaining}")
        self.message_label.config(text=f"Wave {self.current_wave} approaching! {self.enemies_to_spawn_this_wave} enemies.")
        
        self.root.after(self.enemy_spawn_interval, self._spawn_enemy)

    def _spawn_enemy(self):
        if not self.game_running_flag or self.enemies_to_spawn_this_wave <= 0:
            return

        enemy_attack_power = random.randint(5, 15)
        self.village_health -= enemy_attack_power
        
        if self.village_health <= 0:
            self.village_health = 0
            self.health_label.config(text=f"Village Health: {self.village_health}", fg="red")
            self._end_game(win=False)
            return

        self.health_label.config(text=f"Village Health: {self.village_health}", 
                                 fg="red" if self.village_health < 30 else ("orange" if self.village_health < 60 else "green"))

        self.enemies_to_spawn_this_wave -= 1
        self.enemies_remaining -= 1
        self.enemies_label.config(text=f"Enemies Remaining: {self.enemies_remaining}")

        if self.enemies_remaining > 0 or self.enemies_to_spawn_this_wave > 0:
            self.root.after(self.enemy_spawn_interval, self._spawn_enemy)
        elif self.enemies_remaining == 0 and self.enemies_to_spawn_this_wave == 0:
            self.root.after(1000, self._wave_clear)

    def _wave_clear(self):
        if not self.game_running_flag:
            return
        self.message_label.config(text=f"Wave {self.current_wave} repelled!")
        self.root.after(2000, self._next_wave)


    def _end_game(self, win=False):
        self.game_running_flag = False
        if win:
            messagebox.showinfo("Victory!", f"You successfully defended the village through {self.current_wave} waves!")
        else:
            messagebox.showerror("Defeat!", f"The village has fallen after {self.current_wave} waves. Your health reached 0.")
        self.start_button.config(text="Restart Defense", state=tk.NORMAL)
        self.message_label.config(text="Press Restart Defense to try again!")


if __name__ == "__main__":
    game = HokageDefenseGame()
    game.run()