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

def custom_messagebox(title, message, box_type="info"): 
    custom_box = tk.Toplevel(root)
    custom_box.title(title)
    custom_box.bind("<Escape>", lambda e: root.destroy())  # Allow exiting fullscreen with the Esc key
    custom_box.geometry("600x300+600+200")  # Increase the size of the message box
    custom_box.attributes('-topmost', 'true')  # Make the message box topmost
    custom_box.grab_set()
    custom_box.focus_force()

    msg_label = tk.Label(custom_box, text=message, font=("Helvetica", 18), wraplength=550)
    msg_label.pack(pady=40)  # Increase padding for better touch response

    if box_type == "error":
        button_text = "OK"
        button_command = custom_box.destroy
    elif box_type == "info":
        button_text = "OK"
        button_command = custom_box.destroy
    elif box_type == "askyesno":
        button_frame = tk.Frame(custom_box)
        button_frame.pack(pady=40)  # Increase padding for better touch response
        yes_button = tk.Button(button_frame, text="Yes", font=("Helvetica", 18), width=12, height=3, command=lambda: (custom_box.destroy(), root.quit()))
        yes_button.pack(side=tk.LEFT, padx=20)  # Increase padding for better touch response
        no_button = tk.Button(button_frame, text="No", font=("Helvetica", 18), width=12, height=3, command=custom_box.destroy)
        no_button.pack(side=tk.RIGHT, padx=20)  # Increase padding for better touch response
        return custom_box.wait_window()

    ok_button = tk.Button(custom_box, text=button_text, font=("Helvetica", 18), width=12, height=3, command=button_command)
    ok_button.pack(pady=40)  # Increase padding for better touch response

def save_pins():
    selected_pins = [button['text'] for button in buttons if button.cget("bg") == "#32CD32"]
    article_name = article_name_entry.get()
    if not article_name:
        custom_messagebox("Fel", "Vänligen ange ett artikelnummer.", "error")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, "Artiklar")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, f"{article_name}.txt")

    if os.path.exists(file_path):
        if not custom_messagebox("Artikeln finns", f"En artikel med namnet '{article_name}.txt' finns redan. Vill du spara över den?", "askyesno"):
            return

    with open(file_path, "w") as file:
        for pin in selected_pins:
            file.write(pin + "\n")

    custom_messagebox("Färdig", "Artikel Sparad.", "info")






# Initialize main window
root = tk.Tk()
root.title("Skapa Artikel")
root.geometry("1920x1080")
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.destroy())  # Allow exiting fullscreen with the Esc key

# Ensure the window is brought to the front
root.lift()
root.attributes('-topmost', True)
root.after(100, lambda: root.attributes('-topmost', False, '-fullscreen', True))

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
    select_all_button = tk.Button(col_frame, text=f"Selektera Rad", font=body_font, command=lambda c=col: select_all_column(c), bg="light gray")
    select_all_button.pack(pady=5)
    for row in range(8):
        idx = row + col * 8
        button = tk.Button(col_frame, text=pins[idx], font=body_font, width=10, height=2,
                           command=lambda b=idx: toggle_button(buttons[b]), bg="light gray")
        button.pack(pady=5)
        buttons.append(button)

# Save Button
save_button = tk.Button(root, text="Spara", font=body_font, bg="#32CD32", fg="black", command=save_pins, width=10, height=6)
save_button.pack(side=tk.BOTTOM, pady=60)

def show_keyboard(entry_widget, on_submit=None, message="Enter input:"):
    keyboard_window = tk.Toplevel(root, bg="#0A60C5")
    keyboard_window.title("On-Screen Keyboard")
    keyboard_window.geometry("1920x1080")
    keyboard_window.attributes('-fullscreen', True)
    keyboard_window.resizable(False, False)
    keyboard_window.overrideredirect(True)  # Remove the window frame
    keyboard_window.grab_set()

    def insert_char(char):
        entry_field.insert(tk.END, char)

    # Add message label
    message_label = tk.Label(keyboard_window, text=message, font=("Helvetica", 24), bg="#0A60C5", fg="white")
    message_label.pack(pady=20)

    # Add entry widget for input
    entry_field = tk.Entry(keyboard_window, font=("Helvetica", 24))
    entry_field.pack(pady=10)

    main_frame = tk.Frame(keyboard_window, bg="#0A60C5")
    main_frame.pack(pady=20)

    key_frame = tk.Frame(main_frame, bg="#0A60C5")
    key_frame.grid(row=0, column=0, pady=20)

    numpad_frame = tk.Frame(main_frame, bg="#0A60C5")
    numpad_frame.grid(row=0, column=1, padx=20, pady=20, sticky='n')

    keys = [
        'QWERTYUIOP',
        'ASDFGHJKL',
        'ZXCVBNM'
    ]

    # Arrange keys in the keyboard window
    for key_row in keys:
        row_frame = tk.Frame(key_frame, bg="#0A60C5")
        row_frame.pack(side=tk.TOP, pady=5)
        for char in key_row:
            button = tk.Button(row_frame, text=char, font=("Helvetica", 18), width=6, height=4, command=lambda c=char: insert_char(c))
            button.pack(side=tk.LEFT, padx=5)

    space_button = tk.Button(key_frame, text="SPACE", font=("Helvetica", 18), width=60, height=2, command=lambda: insert_char(" "))
    space_button.pack(pady=10)

    # Arrange numpad keys in the keyboard window
    numpad_keys = [
        '789',
        '456',
        '123',
        '0+-'
    ]

    for i, key_row in enumerate(numpad_keys):
        row_frame = tk.Frame(numpad_frame, bg="#0A60C5")
        row_frame.pack(pady=5)
        for char in key_row:
            button = tk.Button(row_frame, text=char, font=("Helvetica", 18), width=6, height=4, command=lambda c=char: insert_char(c))
            button.pack(side=tk.LEFT, padx=5)

    bottom_frame = tk.Frame(numpad_frame, bg="#0A60C5")
    bottom_frame.pack(pady=5)

    close_button = tk.Button(bottom_frame, text="X", font=("Helvetica", 18), width=6, height=4, command=keyboard_window.destroy, bg="red")
    close_button.pack(side=tk.LEFT, padx=5)

    if on_submit is None:
        # Default behavior: just destroy the window without doing anything
        on_submit = lambda entry_value, win: win.destroy()

    submit_button = tk.Button(bottom_frame, text="Submit", font=("Helvetica", 18), width=6, height=4, command=lambda: on_submit(entry_field.get(), keyboard_window))
    submit_button.pack(side=tk.LEFT, padx=5)

    # Pre-fill the entry field if there's any initial text
    entry_field.insert(0, entry_widget.get())

    # Set focus to the entry field
    entry_field.focus()





root.mainloop()
