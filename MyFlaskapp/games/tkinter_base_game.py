import tkinter as tk
from tkinter import messagebox

class BaseGame:
    def __init__(self, title="Game", width=600, height=400):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.game_running = False

    def setup_ui(self):
        # This method should be overridden by child classes to set up game-specific UI
        pass

    def start_game(self):
        self.game_running = True
        messagebox.showinfo("Game Start", "Game has started!")

    def end_game(self):
        self.game_running = False
        messagebox.showinfo("Game Over", "Game has ended!")
        self.root.destroy()

    def run(self):
        self.setup_ui()
        self.root.mainloop()

if __name__ == '__main__':
    # Example usage:
    class MyTkinterGame(BaseGame):
        def setup_ui(self):
            label = tk.Label(self.root, text="Hello from a Tkinter Game!")
            label.pack(pady=20)
            start_button = tk.Button(self.root, text="Start Game", command=self.start_game)
            start_button.pack()
            end_button = tk.Button(self.root, text="End Game", command=self.end_game)
            end_button.pack()

    game = MyTkinterGame("My Awesome Tkinter Game")
    game.run()