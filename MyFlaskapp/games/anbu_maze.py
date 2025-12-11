import tkinter as tk
from tkinter import messagebox
from tkinter_base_game import BaseGame as TkinterBaseGame

class AnbuMazeGame(TkinterBaseGame):
    def __init__(self, master=None):
        super().__init__("Anbu Maze", width=500, height=550) # Adjusted height for messages
        self.maze_data = [
            ["#", "#", "#", "#", "#", "#", "#", "#"],
            ["#", "S", " ", " ", " ", " ", " ", "#"],
            ["#", "#", "#", " ", "#", "#", " ", "#"],
            ["#", " ", " ", " ", "#", " ", " ", "#"],
            ["#", " ", "#", "#", "#", " ", "#", "#"],
            ["#", " ", " ", " ", " ", " ", " ", "#"],
            ["#", "#", " ", "#", "#", "#", "E", "#"],
            ["#", "#", "#", "#", "#", "#", "#", "#"]
        ]
        self.cell_size = 50
        self.player_pos = [0, 0] # Will be updated by _find_start
        self.game_running_flag = False
        self.master = master

    def setup_ui(self):
        self.title_label = tk.Label(self.root, text="Anbu Maze!", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=len(self.maze_data[0]) * self.cell_size,
                                height=len(self.maze_data) * self.cell_size, bg="black")
        self.canvas.pack()

        self.message_label = tk.Label(self.root, text="Press Start to begin!", font=("Arial", 12))
        self.message_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Game", command=self._start_game, font=("Arial", 12))
        self.start_button.pack(pady=5)

        # Bind arrow keys for movement
        self.root.bind("<Up>", lambda event: self._move_player_gui('w'))
        self.root.bind("<Down>", lambda event: self._move_player_gui('s'))
        self.root.bind("<Left>", lambda event: self._move_player_gui('a'))
        self.root.bind("<Right>", lambda event: self._move_player_gui('d'))

    def _find_start(self):
        for r_idx, row in enumerate(self.maze_data):
            for c_idx, cell in enumerate(row):
                if cell == "S":
                    return [r_idx, c_idx]
        return [0,0] # Should not happen if maze is well-formed

    def _draw_maze(self):
        self.canvas.delete("all")
        for r_idx, row in enumerate(self.maze_data):
            for c_idx, cell in enumerate(row):
                x1, y1 = c_idx * self.cell_size, r_idx * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                if cell == "#":
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="gray", outline="darkgray")
                elif cell == " ":
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="lightgray")
                elif cell == "E":
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="darkgreen")
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, text="E", fill="white", font=("Arial", 16))
        
        # Draw player
        pr, pc = self.player_pos
        px1, py1 = pc * self.cell_size + self.cell_size // 4, pr * self.cell_size + self.cell_size // 4
        px2, py2 = (pc + 1) * self.cell_size - self.cell_size // 4, (pr + 1) * self.cell_size - self.cell_size // 4
        self.canvas.create_oval(px1, py1, px2, py2, fill="red", outline="darkred", tags="player")

    def _start_game(self):
        self.player_pos = self._find_start()
        self.game_running_flag = True
        self.start_button.config(state=tk.DISABLED)
        self.message_label.config(text="Use arrow keys to navigate.")
        self._draw_maze()
        self.root.focus_set() # Allow key presses to be registered

    def _move_player_gui(self, direction):
        if not self.game_running_flag:
            return

        r, c = self.player_pos
        new_r, new_c = r, c

        if direction == 'w': # Up
            new_r -= 1
        elif direction == 's': # Down
            new_r += 1
        elif direction == 'a': # Left
            new_c -= 1
        elif direction == 'd': # Right
            new_c += 1

        # Check boundaries and walls
        if 0 <= new_r < len(self.maze_data) and 0 <= new_c < len(self.maze_data[0]) and self.maze_data[new_r][new_c] != '#':
            self.player_pos = [new_r, new_c]
            self._draw_maze() # Redraw maze with new player position

            if self.maze_data[new_r][new_c] == 'E':
                self._end_game(win=True)
        else:
            self.message_label.config(text="Blocked!")
            self.root.after(500, lambda: self.message_label.config(text="")) # Clear message after a short delay

    def _end_game(self, win=False):
        self.game_running_flag = False
        if win:
            messagebox.showinfo("Congratulations!", "You've successfully found the exit!")
        else:
            messagebox.showinfo("Game Over", "You quit the mission.")
        self.start_button.config(text="Play Again", state=tk.NORMAL)
        self.message_label.config(text="Press Play Again to start a new maze!")


if __name__ == "__main__":
    game = AnbuMazeGame()
    game.run()