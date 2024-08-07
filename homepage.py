import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import subprocess
import os
import sys

# Function to navigate to the home page
def go_home():
    # Code to navigate to the home page
    pass

# Functions to navigate to respective pages
def load_article():
    # Run the load_article.py script using the same Python interpreter and environment
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "load_article.py")])

def create_article():
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "create_article.py")])

# Initialize main window
root = tk.Tk()
root.title("Home")
root.geometry("1920x1080")
root.attributes('-fullscreen', True)

# Ensure the window is brought to the front
root.lift()
root.attributes('-topmost', True)
root.after(10, lambda: root.attributes('-topmost', False))

# Custom Fonts
header_font = font.Font(family="Helvetica", size=24, weight="bold")
button_font = font.Font(family="Helvetica", size=36, weight="bold")

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the image file inside the PI folder
logo_path = os.path.join(script_dir, "logo.png")

# Open and resize the image
image = Image.open(logo_path)
scale_percent = 50  # percent of original size
width, height = image.size
new_width = int(width * scale_percent / 100)
new_height = int(height * scale_percent / 100)
resized_image = image.resize((new_width, new_height), Image.LANCZOS)
logo_image = ImageTk.PhotoImage(resized_image)


# Header Section with Logo
header_frame = tk.Frame(root)
header_frame.pack(side=tk.TOP, fill=tk.X)

logo_label = tk.Label(header_frame, image=logo_image)
logo_label.pack(side=tk.LEFT, padx=10, pady=10)
logo_label.bind("<Button-1>", lambda e: go_home())  # go_home function to be defined for navigation

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(expand=True)

buttons = [
    ("Ladda artikel", "#32CD32", load_article),
    ("Skapa ny artikel", "#9900AB", create_article),
]

for text, color, command in buttons:
    button = tk.Button(button_frame, text=text, font=button_font, bg=color, fg="black", command=command, width=15, height=5)
    button.pack(pady=20, padx=10, fill=tk.X)

root.mainloop()
