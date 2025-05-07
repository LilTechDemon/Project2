import tkinter as tk
from tkinter import simpledialog, colorchooser
import random
import csv
import os

# Constants for the game
WIDTH = 500  # Width of the game canvas
HEIGHT = 500  # Height of the game canvas
SPEED = 150  # Speed of the game (in milliseconds)
SPACE_SIZE = 20  # Size of each grid space
BODY_SIZE = 2  # Initial size of the snake
FOOD_COLOR = "#ff0155"  # Color of the food
BACKGROUND_COLOR = "#000000"  # Background color of the canvas
LEADERBOARD_FILE = "leaderboard.csv"  # File to store leaderboard data

class SnakeGame:
    """
    A class representing the Snake Game.
    Handles the game logic, UI, and interactions.
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the SnakeGame instance.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        # Initialize the root window and game variables
        self.root = root
        self.root.title("Snake Game")  # Set the window title
        self.snake_color = "#00ffaa"  # Default snake color
        self.running = False  # Game running state
        self.paused = False  # Game paused state
        self.player_name = ""  # Player's name
        self.main_menu()  # Show the main menu

    def main_menu(self):
        """
        Display the main menu of the game.
        Allows the player to enter their name, choose a snake color, and start the game.
        """
        self.clear_window()  # Clear any existing widgets from the window

        # Create a canvas to preview the snake and food
        self.preview_canvas = tk.Canvas(
            self.root, width=400, height=100, bg=BACKGROUND_COLOR,
            highlightthickness=1, highlightbackground="gray"
        )
        self.preview_canvas.pack(pady=20)  # Add padding around the canvas
        self.draw_color_preview()  # Draw the initial preview of the snake and food

        # Add the game title
        title = tk.Label(self.root, text="Snake Game", font=("consolas", 30))
        title.pack(pady=10)

        # Input field for the player's name
        name_label = tk.Label(self.root, text="Enter your name (1–3 letters):")
        name_label.pack()
        self.name_entry = tk.Entry(self.root, justify="center", font=("consolas", 14))
        self.name_entry.pack(pady=5)

        # Button to choose the snake's color
        color_button = tk.Button(self.root, text="Choose Snake Color", command=self.choose_color)
        color_button.pack(pady=(10, 20))

        # Frame to hold the Start Game and Leaderboard buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack()

        # Button to start the game
        start_button = tk.Button(button_frame, text="Start Game", width=15, command=self.start_game)
        start_button.grid(row=0, column=0, padx=10)

        # Button to view the leaderboard
        leaderboard_button = tk.Button(button_frame, text="Leaderboard", width=15, command=self.view_leaderboard)
        leaderboard_button.grid(row=0, column=1, padx=10)

        # Button to view the game instructions
        instructions_button = tk.Button(self.root, text="View Instructions", width=32, command=self.instructions_screen)
        instructions_button.pack(pady=(20, 10))

    def choose_color(self):
        """
        Open a color chooser dialog to select the snake's color.
        Updates the preview canvas with the selected color.
        """
        # Open a color chooser dialog and get the selected color
        color = colorchooser.askcolor(title="Pick Snake Color")[1]
        if color:
            self.snake_color = color  # Update the snake's color
            self.draw_color_preview()  # Redraw the preview with the new color

    def draw_color_preview(self):
        """
        Draw a preview of the snake and food on the preview canvas.
        """
        if hasattr(self, 'preview_canvas'):  # Ensure the preview canvas exists
            self.preview_canvas.delete("all")  # Clear the canvas

            # Draw the snake blocks
            self.preview_canvas.create_rectangle(60, 30, 80, 50, fill=self.snake_color, outline="")
            self.preview_canvas.create_rectangle(82, 30, 102, 50, fill=self.snake_color, outline="")
            self.preview_canvas.create_rectangle(104, 30, 124, 50, fill=self.snake_color, outline="")
            self.preview_canvas.create_rectangle(126, 30, 144, 50, fill=self.snake_color, outline="")

            # Draw the food
            self.preview_canvas.create_oval(300, 30, 320, 50, fill=FOOD_COLOR, outline="")

    def clear_window(self):
        """
        Clear all widgets from the root window.
        """
        for widget in self.root.winfo_children():  # Iterate over all widgets in the window
            widget.destroy()  # Remove each widget

    def start_game(self, player_name=None, snake_color=None):
        """
        Start the game with the given player name and snake color.

        Args:
            player_name (str, optional): The player's name. Defaults to None.
            snake_color (str, optional): The snake's color. Defaults to None.
        """
        # Set the player's name
        if player_name is None:
            self.player_name = self.name_entry.get().strip().upper() or "PLAYER"
        else:
            self.player_name = player_name.upper()

        # Set the snake's color
        if snake_color is None:
            self.snake_color = self.snake_color or "#00ffaa"
        else:
            self.snake_color = snake_color

        # Initialize game variables
        self.score = 0
        self.direction = 'down'
        self.running = True
        self.paused = False

        self.clear_window()  # Clear the main menu

        # Add a label to display the player's score and lives
        self.label = tk.Label(self.root, text="", font=('consolas', 16))
        self.label.pack()

        # Create the game canvas
        self.canvas = tk.Canvas(self.root, bg=BACKGROUND_COLOR, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        # Add a pause button
        self.pause_button = tk.Button(self.root, text="Pause", command=self.toggle_pause)
        self.pause_button.pack()

        # Add a button to return to the main menu
        self.restart_button = tk.Button(self.root, text="Main Menu", command=self.main_menu)
        self.restart_button.pack()

        # Create the snake and food objects
        self.snake = self.Snake(self.canvas, self.snake_color)
        self.food = self.Food(self.canvas)

        # Bind arrow keys to change the snake's direction
        self.root.bind('<Left>', lambda event: self.change_direction('left'))
        self.root.bind('<Right>', lambda event: self.change_direction('right'))
        self.root.bind('<Up>', lambda event: self.change_direction('up'))
        self.root.bind('<Down>', lambda event: self.change_direction('down'))

        self.next_turn()  # Start the game loop

    class Snake:
        """
        A class representing the snake in the game.
        """

        def __init__(self, canvas: tk.Canvas, color: str):
            """
            Initialize the Snake instance.

            Args:
                canvas (tk.Canvas): The canvas where the snake is drawn.
                color (str): The color of the snake.
            """
            self.canvas = canvas
            self.coordinates = [[0, 0] for _ in range(BODY_SIZE)]
            self.squares = []
            for x, y in self.coordinates:
                square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=color, tag="snake")
                self.squares.append(square)
            self.color = color

    class Food:
        """
        A class representing the food in the game.
        """

        def __init__(self, canvas: tk.Canvas):
            """
            Initialize the Food instance.

            Args:
                canvas (tk.Canvas): The canvas where the food is drawn.
            """
            x = random.randint(0, (WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
            y = random.randint(0, (HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
            self.coordinates = [x, y]
            canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=FOOD_COLOR, tag="food")

    def change_direction(self, new_direction: str):
        """
        Change the direction of the snake.

        Args:
            new_direction (str): The new direction ('up', 'down', 'left', 'right').
        """
        opposites = {'left': 'right', 'right': 'left', 'up': 'down', 'down': 'up'}
        if new_direction != opposites.get(self.direction):
            self.direction = new_direction

    def next_turn(self):
        """
        Execute the next turn of the game.
        Moves the snake, checks for collisions, and updates the game state.
        """
        if not self.running or self.paused:
            return

        x, y = self.snake.coordinates[0]
        if self.direction == 'up':
            y -= SPACE_SIZE
        elif self.direction == 'down':
            y += SPACE_SIZE
        elif self.direction == 'left':
            x -= SPACE_SIZE
        elif self.direction == 'right':
            x += SPACE_SIZE

        new_head = [x, y]
        self.snake.coordinates.insert(0, new_head)
        square = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=self.snake.color)
        self.snake.squares.insert(0, square)

        if new_head == self.food.coordinates:
            self.score += 1
            self.canvas.delete("food")
            self.food = self.Food(self.canvas)
        else:
            self.snake.coordinates.pop()
            self.canvas.delete(self.snake.squares.pop())

        if self.check_collisions():
            if len(self.snake.coordinates) > 1:
                self.canvas.delete(self.snake.squares.pop())
                self.snake.coordinates.pop()
            else:
                self.save_score()
                self.game_over()
                return

        self.lives = len(self.snake.coordinates)
        self.label.config(text=f"{self.player_name} - Score: {self.score} | Lives: {self.lives}")
        self.root.after(SPEED, self.next_turn)

    def check_collisions(self):
        """
        Check if the snake has collided with the wall or itself.

        Returns:
            bool: True if a collision occurred, False otherwise.
        """
        x, y = self.snake.coordinates[0]
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return True
        for body in self.snake.coordinates[1:]:
            if x == body[0] and y == body[1]:
                return True
        return False

    def save_score(self):
        """
        Save the player's score to the leaderboard.
        Updates the leaderboard file with the player's recent and high scores.
        """
        leaderboard_exists = os.path.exists(LEADERBOARD_FILE)

        if not leaderboard_exists:
            with open(LEADERBOARD_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Recent', 'High'])

        with open(LEADERBOARD_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            valid_rows = list(reader)

        player_found = False
        for row in valid_rows:
            if row["Name"] == self.player_name:
                row["Recent"] = self.score
                if self.score > int(row["High"]):
                    row["High"] = self.score
                player_found = True
                break

        if not player_found:
            valid_rows.append({
                'Name': self.player_name,
                'Recent': self.score,
                'High': self.score
            })

        with open(LEADERBOARD_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Name', 'Recent', 'High'])
            writer.writeheader()
            writer.writerows(valid_rows)

    def game_over(self):
        """
        Handle the game over state.
        Displays the "GAME OVER" text and buttons to restart or return to the main menu.
        """
        self.running = False
        self.canvas.delete(tk.ALL)

        # Create a frame for the "GAME OVER" text and buttons
        game_over_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        game_over_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame in the middle of the window

        # Display "GAME OVER" text at the center of the canvas
        game_over_text = tk.Label(game_over_frame, text="GAME OVER", font=('consolas', 40), fg="red", bg=BACKGROUND_COLOR)
        game_over_text.pack(pady=20)  # Padding between text and buttons

        # Create a frame for the buttons (Restart and Main Menu)
        button_frame = tk.Frame(game_over_frame, bg=BACKGROUND_COLOR)
        button_frame.pack(pady=20)

        # Restart button
        restart_btn = tk.Button(button_frame, text="Restart", font=("consolas", 14), command=self.restart_game)
        restart_btn.grid(row=0, column=0, padx=10)

        # Main Menu button
        main_menu_btn = tk.Button(button_frame, text="Main Menu", font=("consolas", 14), command=self.main_menu)
        main_menu_btn.grid(row=0, column=1, padx=10)

    def restart_game(self):
        """
        Restart the game with the current player's name and snake color.
        """
        self.start_game(self.player_name, self.snake_color)

    def toggle_pause(self):
        """
        Toggle the pause state of the game.
        """
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")
        if not self.paused:
            self.next_turn()

    def view_leaderboard(self):
        """
        Display the leaderboard with the top scores.
        """
        self.clear_window()
        tk.Label(self.root, text="Leaderboard", font=("consolas", 24)).pack(pady=10)

        if not os.path.exists(LEADERBOARD_FILE):
            tk.Label(self.root, text="No scores yet.").pack()
        else:
            with open(LEADERBOARD_FILE, "r") as file:
                reader = csv.DictReader(file)
                valid_rows = []
                for row in reader:
                    try:
                        if row["High"] and row["High"].strip():
                            row["High"] = int(row["High"])
                            valid_rows.append(row)
                    except (ValueError, TypeError):
                        continue

            valid_rows.sort(key=lambda row: row["High"], reverse=True)
            top_10 = valid_rows[:10]

            for i, row in enumerate(top_10, start=1):
                name = row["Name"]
                recent = row["Recent"]
                high = row["High"]
                tk.Label(self.root, text=f"{i}. {name} - Recent: {recent} - High: {high}", font=("consolas", 14)).pack()

        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=10)

    def instructions_screen(self):
        """
        Display the instructions for playing the game.
        """
        self.clear_window()

        tk.Label(self.root, text="Instructions", font=("consolas", 24)).pack(pady=10)

        instructions = (
            "- Use the arrow keys to move the snake.\n"
            "- Eat the pink food to grow and score points.\n"
            "- Avoid running into walls or yourself.\n"
            "- You lose a 'life' (body segment) on collision.\n"
            "- The game ends when no segments remain.\n"
            "- Pause the game anytime using the Pause button.\n"
            "- Your score and name will appear on the leaderboard.\n"
            "\nTip: Use 1–3 letter name before starting!"
        )

        tk.Label(self.root, text=instructions, justify="left", font=("consolas", 14)).pack(padx=20, pady=10)

        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=10)