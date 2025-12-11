import tkinter as tk
from tkinter import messagebox
import random
from tkinter_base_game import BaseGame as TkinterBaseGame

class NinjaTriviaGame(TkinterBaseGame):
    def __init__(self, master=None):
        super().__init__("Ninja Trivia", width=600, height=500)
        self.questions = [
            {
                "question": "Which village does Naruto Uzumaki belong to?",
                "options": ["Hidden Cloud", "Hidden Leaf", "Hidden Mist", "Hidden Sand"],
                "answer": "Hidden Leaf"
            },
            {
                "question": "What is the name of Naruto's signature jutsu?",
                "options": ["Chidori", "Rasengan", "Susanoo", "Amaterasu"],
                "answer": "Rasengan"
            },
            {
                "question": "Who is the leader of the Akatsuki?",
                "options": ["Itachi", "Obito", "Pain", "Kisame"],
                "answer": "Pain"
            },
            {
                "question": "What is Sakura Haruno's main medical ninja teacher?",
                "options": ["Tsunade", "Shizune", "Kakashi", "Jiraiya"],
                "answer": "Tsunade"
            },
            {
                "question": "Which Uchiha awakened the Mangekyo Sharingan after witnessing his best friend's death?",
                "options": ["Madara", "Sasuke", "Itachi", "Obito"],
                "answer": "Obito"
            },
            {
                "question": "What is the name of the tailed beast sealed inside Naruto?",
                "options": ["Shukaku", "Matatabi", "Kurama", "Gyuki"],
                "answer": "Kurama"
            },
            {
                "question": "Which sensei leads Team Guy?",
                "options": ["Kakashi Hatake", "Might Guy", "Asuma Sarutobi", "Kurenai Yuhi"],
                "answer": "Might Guy"
            },
            {
                "question": "What is the name of Rock Lee's primary fighting style?",
                "options": ["Ninjutsu", "Genjutsu", "Taijutsu", "Senjutsu"],
                "answer": "Taijutsu"
            },
            {
                "question": "Who trained Naruto in Sage Mode?",
                "options": ["Jiraiya", "Fukasaku", "Hiruzen Sarutobi", "Tsunade"],
                "answer": "Fukasaku"
            },
            {
                "question": "What is the primary goal of the Akatsuki?",
                "options": ["World domination", "Peace through pain", "Collecting tailed beasts", "Destroying Konoha"],
                "answer": "Collecting tailed beasts"
            }
        ]
        self.current_question_index = 0
        self.score = 0
        self.game_running_flag = False
        self.selected_option = tk.StringVar(self.root)
        self.master = master # Store master if this game is part of a larger app

    def setup_ui(self):
        self.title_label = tk.Label(self.root, text="Ninja Trivia!", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)

        self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=("Arial", 14))
        self.score_label.pack(pady=5)

        self.question_label = tk.Label(self.root, text="Press Start to begin!", font=("Arial", 12), wraplength=550)
        self.question_label.pack(pady=10)

        self.option_buttons = []
        for i in range(4):
            btn = tk.Radiobutton(self.root, text=f"Option {i+1}", variable=self.selected_option, value="",
                                 font=("Arial", 10), anchor="w", state=tk.DISABLED)
            btn.pack(fill="x", padx=50, pady=2)
            self.option_buttons.append(btn)

        self.submit_button = tk.Button(self.root, text="Submit Answer", command=self._check_answer, state=tk.DISABLED,
                                       font=("Arial", 12))
        self.submit_button.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Game", command=self._start_game, font=("Arial", 12))
        self.start_button.pack(pady=10)

    def _start_game(self):
        self.score = 0
        self.current_question_index = 0
        random.shuffle(self.questions)
        self.score_label.config(text=f"Score: {self.score}")
        self.start_button.config(state=tk.DISABLED)
        self.game_running_flag = True
        self._load_question()

    def _load_question(self):
        if self.current_question_index < len(self.questions):
            q = self.questions[self.current_question_index]
            self.question_label.config(text=f"Question {self.current_question_index + 1}: {q['question']}")
            self.selected_option.set("") # Clear previous selection

            for i, option in enumerate(q['options']):
                self.option_buttons[i].config(text=option, value=option, state=tk.NORMAL)
            self.submit_button.config(state=tk.NORMAL)
        else:
            self._end_game()

    def _check_answer(self):
        if not self.game_running_flag:
            return

        selected = self.selected_option.get()
        current_q = self.questions[self.current_question_index]

        for btn in self.option_buttons:
            btn.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)

        if selected == current_q['answer']:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            messagebox.showinfo("Correct!", "You got it right!")
        else:
            messagebox.showerror("Incorrect!", f"The correct answer was: {current_q['answer']}")
        
        self.current_question_index += 1
        self.root.after(1000, self._load_question) # Load next question after a delay

    def _end_game(self):
        self.game_running_flag = False
        messagebox.showinfo("Trivia Complete!", f"Your final score: {self.score}/{len(self.questions)}")
        self.start_button.config(text="Play Again", state=tk.NORMAL)
        self.question_label.config(text="Thanks for playing!")
        for btn in self.option_buttons:
            btn.config(text="", value="", state=tk.DISABLED)


if __name__ == "__main__":
    game = NinjaTriviaGame()
    game.run()