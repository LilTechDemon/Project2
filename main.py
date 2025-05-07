import tkinter as tk
from logic import SnakeGame

def main():
    root = tk.Tk()
    root.title("Snake Game")
    game = SnakeGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()

