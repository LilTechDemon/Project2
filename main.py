import tkinter as tk
from logic import SnakeGame

# base code/ idea from https://www.geeksforgeeks.org/snake-game-using-tkinter-python/

def main():
    root = tk.Tk()
    root.title("Snake Game")
    game = SnakeGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()

