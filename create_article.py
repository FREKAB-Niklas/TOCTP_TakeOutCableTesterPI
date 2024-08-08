import tkinter as tk
from tkinter import font
from tkinter import messagebox
from PIL import Image, ImageTk
import os



# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the image file inside the PI folder
logo_path = os.path.join(script_dir, "logo.png")

def toggle_button(button):
    current_color = button.cget("bg")
    new_color = "#32CD32" if current_color == "light gray" else "light gray"
    button.config(bg=new_color)

def select_all_column(col_idx):
    for i in range(8):
        idx = col_idx * 8 + i
        toggle_button(buttons[idx])

def save_pins():
    selected_pins = [button['text'] for button in buttons if button.cget("bg") == "#32CD32"]
    article_name = article_name_entry.get()
    if not article_name:
        messagebox.showerror("Error", "Please enter the article name.")
        return

    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the 'Artiklar' directory inside the PI folder
    folder_path = os.path.join(script_dir, "Artiklar")

    # Check if the directory exists, if not, create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, f"{article_name}.txt")

    # Check if the file already exists
    if os.path.exists(file_path):
        overwrite = messagebox.askyesno("File Exists", f"A file named '{article_name}.txt' already exists. Do you want to overwrite it?")
        if not overwrite:
            return

    with open(file_path, "w") as file:
        for pin in selected_pins:
            file.write(pin + "\n")

    messagebox.showinfo("Success", "Pins saved successfully.")




# Initialize main window
root = tk.Tk()
root.title("Create New Article")
root.geometry("1920x1080")
root.attributes('-fullscreen', True)

# Ensure the window is brought to the front
root.lift()
root.attributes('-topmost', True)
root.after(10, lambda: root.attributes('-topmost', False))

# Custom Fonts
header_font = font.Font(family="Helvetica", size=24, weight="bold")
body_font = font.Font(family="Helvetica", size=16)


# Open and resize the image
image = Image.open(logo_path)
scale_percent = 50  # percent of original size
width, height = image.size
new_width = int(width * scale_percent / 100)
new_height = int(height * scale_percent / 100)
resized_image = image.resize((new_width, new_height), Image.LANCZOS)
logo_image = ImageTk.PhotoImage(resized_image)


# Header Section
header_frame = tk.Frame(root)
header_frame.pack(side=tk.TOP, fill=tk.X)

logo_label = tk.Label(header_frame, image=logo_image)
logo_label.pack(side=tk.LEFT, padx=10, pady=10)
logo_label.bind("<Button-1>", lambda e: root.destroy())  # Temporary function to close the app

# Text Entry for Article Name
article_name_label = tk.Label(header_frame, text="Artikelnummer:", font=body_font)
article_name_label.pack(side=tk.LEFT, padx=10)
article_name_entry = tk.Entry(header_frame, font=body_font)
article_name_entry.pack(side=tk.LEFT, padx=10)
article_name_entry.bind("<Button-1>", lambda e: show_keyboard(article_name_entry))

# Pin Selection Section
pins_frame = tk.Frame(root)
pins_frame.pack(pady=20)

pins = [
    "1: A", "2: B", "3: C", "4: D", "5: E", "6: F", "7: G", "8: H", "9: J",
    "10: K", "11: L", "12: M", "13: N", "14: P", "15: R", "16: S", "17: T",
    "18: U", "19: V", "20: W", "21: X", "22: Y", "23: Z", "24: a", "25: b",
    "26: c", "27: d", "28: e", "29: f", "30: g", "31: h", "32: j"
]

buttons = []
for col in range(4):
    col_frame = tk.Frame(pins_frame)
    col_frame.grid(row=0, column=col, padx=10)
    select_all_button = tk.Button(col_frame, text=f"Selektera Rad", font=body_font, command=lambda c=col: select_all_column(c))
    select_all_button.pack(pady=5)
    for row in range(8):
        idx = row + col * 8
        button = tk.Button(col_frame, text=pins[idx], font=body_font, width=10, height=2,
                           command=lambda b=idx: toggle_button(buttons[b]))
        button.pack(pady=5)
        buttons.append(button)

# Save Button
save_button = tk.Button(root, text="Spara", font=body_font, bg="#32CD32", fg="black", command=save_pins, width=10, height=6)
save_button.pack(side=tk.BOTTOM, pady=60)

def show_keyboard(entry_widget):
    keyboard_window = tk.Toplevel(root, bg="#0A60C5")
    keyboard_window.title("On-Screen Keyboard")
    keyboard_window.geometry("1600x850+250+180")
    keyboard_window.resizable(False, False)
    keyboard_window.overrideredirect(True)  # Remove the window frame

    def insert_char(char):
        entry_widget.insert(tk.END, char)

    keys = [
        'QWERTYUIOP',
        'ASDFGHJKL',
        'ZXCVBNM'
    ]

    # Arrange keys in the keyboard window
    for i, key_row in enumerate(keys):
        row_frame = tk.Frame(keyboard_window, bg="#0A60C5")
        row_frame.grid(row=i, column=0, columnspan=3, pady=5, padx=1)
        for char in key_row:
            button = tk.Button(row_frame, text=char, font=body_font, width=6, height=4, command=lambda c=char: insert_char(c))
            button.pack(side=tk.LEFT, padx=5)

    space_button = tk.Button(keyboard_window, text="SPACE", font=body_font, width=20, height=2, command=lambda: insert_char(" "))
    space_button.grid(row=3, column=0, columnspan=3, pady=5)

    # Arrange numpad keys in the keyboard window
    numpad_keys = [
        '789',
        '456',
        '123',
        '0+-'
    ]

    numpad_frame = tk.Frame(keyboard_window, bg="#0A60C5")
    numpad_frame.grid(row=0, column=4, rowspan=4, padx=100, pady=25)

    for i, key_row in enumerate(numpad_keys):
        row_frame = tk.Frame(numpad_frame, bg="#0A60C5")
        row_frame.pack(pady=5)
        for char in key_row:
            button = tk.Button(row_frame, text=char, font=body_font, width=8, height=5, command=lambda c=char: insert_char(c))
            button.pack(side=tk.LEFT, padx=5)

    close_button = tk.Button(keyboard_window, text="X", font=body_font, width=10, height=5, command=keyboard_window.destroy, bg="red")
    close_button.grid(row=5, column=4, columnspan=3, pady=5)



root.mainloop()
