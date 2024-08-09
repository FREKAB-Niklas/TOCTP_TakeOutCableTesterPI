import tkinter as tk
from tkinter import font, filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import sys
import subprocess
import pandas as pd
from datetime import datetime, timedelta
import openpyxl

previous_selected_row = None
selected_file = None

# Initialize main window
root = tk.Tk()
root.title("Ladda Artikel")
root.geometry("1920x1080")
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.destroy())  # Allow exiting fullscreen with the Esc key

# Ensure the window is brought to the front
root.lift()
root.attributes('-topmost', True)
root.after(100, lambda: root.attributes('-topmost', False, '-fullscreen', True))

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the image file inside the PI folder
logo_path = os.path.join(script_dir, "logo.png")

def run_article(filename, pins):
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the 'run_article.py' script inside the PI folder
    run_article_script_path = os.path.join(script_dir, "run_article.py")
    
    with open("article_config.txt", "w") as config_file:
        config_file.write("[DEFAULT]\n")
        config_file.write(f"filename={filename}\n")
        config_file.write("pins=" + ",".join(pins))
    
    subprocess.run([sys.executable, run_article_script_path])

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

def parse_time_with_decimal(time_str):
    parts = time_str.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    elif len(parts) == 1:
        hours = 0
        minutes = 0
        seconds = parts[0]
    else:
        raise ValueError(f"Invalid time format: {time_str}")
    seconds_float = float(seconds)
    return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds_float), microseconds=int((seconds_float % 1) * 1e6))

def show_log(filename):
    log_filename = filename.replace('.txt', '_log.xlsx')  # Replace .txt with _log.xlsx

    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the 'Artiklar' directory inside the PI folder
    log_filepath = os.path.join(script_dir, "Artiklar", log_filename)

    if not os.path.exists(log_filepath):
        custom_messagebox("Error", f"Log file {log_filename} does not exist.")
        return
    
    df = pd.read_excel(log_filepath)
    
    # Extract header values before cleaning up the DataFrame
    headers = ["Artikelnummer", "AVG. Stycktid", "Senaste Stycktid", "Total Tid", "Total Antal"]
    values = []
    for header in headers:
        if header in df.columns:
            values.append(df.iloc[0][header])
        else:
            values.append("N/A")  # Default value if the column is not found
    
    # Extract 'Total Antal' directly from the cell
    wb = openpyxl.load_workbook(log_filepath)
    ws = wb.active
    total_antal_value = ws['G4'].value
    if total_antal_value is None:
        total_antal_value = "N/A"
    
    # Replace the "Total Antal" value in the values list
    values[-1] = total_antal_value

    # Find the row where "Batchdatum" is located and set it as the header
    batchdatum_row_idx = df[df.iloc[:, 1] == "Batchdatum"].index[0]
    df.columns = df.iloc[batchdatum_row_idx]
    df = df.drop(range(batchdatum_row_idx + 1)).reset_index(drop=True)

    # Drop columns before "Batchdatum"
    drop_columns = df.columns[:df.columns.get_loc("Batchdatum")]
    df = df.drop(columns=drop_columns)
    
    log_window = tk.Toplevel(root)
    log_window.title("Log Data")
    log_window.attributes('-fullscreen', True)
    log_window.after(100, lambda: root.attributes('-topmost', False, '-fullscreen', True))
    
    # Create a Frame for the header
    header_frame = tk.Frame(log_window)
    header_frame.pack(fill=tk.X, padx=10, pady=10)

    # Open and resize the image
    image = Image.open(logo_path)
    scale_percent = 50  # percent of original size
    width, height = image.size
    new_width = int(width * scale_percent / 100)
    new_height = int(height * scale_percent / 100)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    logo_image = ImageTk.PhotoImage(resized_image)

    logo_label = tk.Label(header_frame, image=logo_image)
    logo_label.image = logo_image  # Keep a reference to avoid garbage collection
    logo_label.grid(row=0, column=0, rowspan=2, padx=10)
    logo_label.bind("<Button-1>", lambda e: log_window.destroy())  # Bind logo click to close the window

    # Display header information
    avg_stycktid = values[1]
    senaste_stycktid = values[2]

    # Parse time strings with potential decimal parts
    avg_stycktid_td = parse_time_with_decimal(str(avg_stycktid))
    senaste_stycktid_td = parse_time_with_decimal(str(senaste_stycktid))

    # Determine background color based on comparison
    if senaste_stycktid_td < avg_stycktid_td:
        bg_color = "#32CD32"
    else:
        bg_color = "red"

    # Display header information without swapping positions
    for i, (header, value) in enumerate(zip(headers, values)):
        tk.Label(header_frame, text=header, font=body_font, borderwidth=2, relief="groove", width=20).grid(row=0, column=i+1, padx=2, pady=2)
        label = tk.Label(header_frame, text=value, font=body_font, borderwidth=2, relief="groove", width=20)
        label.grid(row=1, column=i+1, padx=2, pady=2)
        if header == "Senaste Stycktid":
            label.config(bg=bg_color)  # Set background color

    # Create a Treeview for the log data
    tree_frame = tk.Frame(log_window)
    tree_frame.pack(expand=True, fill=tk.BOTH)
    
    tree = ttk.Treeview(tree_frame)
    tree.pack(expand=True, fill=tk.BOTH)
    
    tree["columns"] = list(df.columns)
    tree["show"] = "headings"  # Hide the default first column
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    for index, row in df.iterrows():
        row_id = tree.insert("", "end", values=list(row))
        if index % 2 == 0:
            tree.item(row_id, tags=('evenrow',))
        else:
            tree.item(row_id, tags=('oddrow',))

    tree.tag_configure('evenrow', background='lightgray')
    tree.tag_configure('oddrow', background='white')




def show_custom_error(message):
    error_window = tk.Toplevel(root)
    error_window.title("Error")
    error_window.geometry("400x200")
    error_window.attributes('-topmost', 'true')

    label = tk.Label(error_window, text=message, font=body_font)
    label.pack(pady=20)

    ok_button = tk.Button(error_window, text="OK", font=body_font, command=error_window.destroy)
    ok_button.pack(pady=20)




def load_files():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the 'Artiklar' directory inside the PI folder
    directory = os.path.join(script_dir, "Artiklar")

    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    file_info = []
    for f in files:
        file_path = os.path.join(directory, f)
        modification_time = os.path.getmtime(file_path)
        formatted_date = datetime.fromtimestamp(modification_time).strftime('%y-%m-%d %H:%M')
        file_info.append((f, formatted_date, "[Link]"))
    return file_info


def select_file(row_frame, filename):
    global selected_file, previous_selected_row

    # Reset the background color of the previously selected row if it still exists
    try:
        if previous_selected_row:
            previous_selected_row.config(bg="white")
            for widget in previous_selected_row.winfo_children():
                widget.config(bg="white")
    except tk.TclError:
        pass  # The previous selected row no longer exists

    # Set the background color of the currently selected row
    row_frame.config(bg="#32CD32")
    for widget in row_frame.winfo_children():
        widget.config(bg="#32CD32")

    selected_file = filename
    previous_selected_row = row_frame




def load_article_file():
    if not selected_file:
        show_custom_error("No file selected. Please select a file first.")
        return
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the 'Artiklar' directory inside the PI folder
    file_path = os.path.join(script_dir, "Artiklar", selected_file)
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    filename = os.path.basename(file_path).split('.')[0]
    pins = [line.strip() for line in lines]
    
    run_article(filename, pins)

def show_keyboard(entry_widget, on_submit, message="Enter password to delete file:"):
    keyboard_window = tk.Toplevel(root, bg="#0A60C5")
    keyboard_window.title("On-Screen Keyboard")
    keyboard_window.geometry("1920x1080")
    keyboard_window.attributes('-fullscreen', True)
    keyboard_window.resizable(False, False)
    keyboard_window.overrideredirect(True)  # Remove the window frame

    def insert_char(char):
        entry_field.insert(tk.END, char)

    # Add message label
    message_label = tk.Label(keyboard_window, text=message, font=body_font, bg="#0A60C5", fg="white")
    message_label.pack(pady=20)

    # Add entry widget for input
    entry_field = tk.Entry(keyboard_window, font=body_font)
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
            button = tk.Button(row_frame, text=char, font=body_font, width=6, height=4, command=lambda c=char: insert_char(c))
            button.pack(side=tk.LEFT, padx=5)

    space_button = tk.Button(key_frame, text="SPACE", font=body_font, width=60, height=2, command=lambda: insert_char(" "))
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
            button = tk.Button(row_frame, text=char, font=body_font, width=6, height=4, command=lambda c=char: insert_char(c))
            button.pack(side=tk.LEFT, padx=5)

    bottom_frame = tk.Frame(numpad_frame, bg="#0A60C5")
    bottom_frame.pack(pady=5)

    close_button = tk.Button(bottom_frame, text="X", font=body_font, width=6, height=4, command=keyboard_window.destroy, bg="red")
    close_button.pack(side=tk.LEFT, padx=5)

    submit_button = tk.Button(bottom_frame, text="Submit", font=body_font, width=6, height=4, command=lambda: on_submit(entry_field.get(), keyboard_window))
    submit_button.pack(side=tk.LEFT, padx=5)




def delete_file():
    if not selected_file:
        custom_messagebox("No file selected", "Please select a file first.")
        return

    def on_password_submit(password, keyboard_window):
        if password == "1":
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Construct the full path to the 'Artiklar' directory inside the PI folder
            file_path = os.path.join(script_dir, "Artiklar", selected_file)
            log_file_path = file_path.replace('.txt', '_log.xlsx')  # Path for the log file

            # Remove the main file
            os.remove(file_path)
            
            # Check if the log file exists and remove it
            if os.path.exists(log_file_path):
                os.remove(log_file_path)

            keyboard_window.destroy()
            refresh_file_list()
        else:
            show_custom_error("Incorrect password.")
            keyboard_window.destroy()

    password_entry = tk.Entry(root, show='*')
    show_keyboard(password_entry, on_password_submit, message="Enter password to delete file:")




def refresh_file_list():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    header = tk.Frame(scrollable_frame)
    header.pack(fill=tk.X)

    tk.Label(header, text="Artikelnummer", font=header_font, width=20, anchor="w").grid(row=0, column=0)
    tk.Label(header, text="Datum", font=header_font, width=15, anchor="w").grid(row=0, column=1)
    tk.Label(header, text="Logg", font=header_font, width=10, anchor="w").grid(row=0, column=2)

    files = load_files()
    for i, (filename, date, log) in enumerate(files):
        row_frame = tk.Frame(scrollable_frame, bg="white")
        row_frame.pack(fill=tk.X)
        row_frame.bind("<Button-1>", lambda e, rf=row_frame, f=filename: select_file(rf, f))

        # Remove the .txt extension from filename
        display_filename = filename.split('.')[0]

        filename_label = tk.Label(row_frame, text=display_filename, font=body_font, width=32, anchor="w", bg="white")
        filename_label.grid(row=0, column=0)
        filename_label.bind("<Button-1>", lambda e, rf=row_frame, f=filename: select_file(rf, f))

        date_label = tk.Label(row_frame, text=date, font=body_font, width=24, anchor="w", bg="white")
        date_label.grid(row=0, column=1)
        date_label.bind("<Button-1>", lambda e, rf=row_frame, f=filename: select_file(rf, f))

        load_log_button = tk.Button(row_frame, text="Logg", font=body_font, command=lambda f=filename: show_log(f))
        load_log_button.grid(row=0, column=3)



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

header_frame = tk.Frame(root)
header_frame.grid(row=0, column=0, pady=10, sticky='nw')  # Adjusted to be top left

logo_label = tk.Label(header_frame, image=logo_image)
logo_label.pack(side=tk.LEFT, padx=10, pady=0)
logo_label.bind("<Button-1>", lambda e: root.destroy())

canvas = tk.Canvas(root, width=800, height=800)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview, width=30)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Center the canvas and scrollbar
canvas.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky='n')  # Adjusted to be in the center
scrollbar.grid(row=1, column=3, sticky='nsw')  # Directly to the right of the canvas

header = tk.Frame(scrollable_frame)
header.pack(fill=tk.X, padx=20, pady=10)

tk.Label(header, text="Artikelnummer", font=header_font, width=20, anchor="w").grid(row=0, column=0)
tk.Label(header, text="Datum", font=header_font, width=15, anchor="w").grid(row=0, column=1)
tk.Label(header, text="Logg", font=header_font, width=10, anchor="w").grid(row=0, column=2)

files = load_files()
for i, (filename, date, log) in enumerate(files):
    row_frame = tk.Frame(scrollable_frame)
    row_frame.pack(fill=tk.X)
    row_frame.bind("<Button-1>", lambda e, rf=row_frame, f=filename: select_file(rf, f))

    tk.Label(row_frame, text=filename, font=body_font, width=200, anchor="w", bg="white").grid(row=0, column=0, sticky='w')
    tk.Label(row_frame, text=date, font=body_font, width=15, anchor="w", bg="white").grid(row=1, column=4, sticky="E")
    # Assuming script_dir and folder_path are already defined as shown in the previous responses
    load_log_button = tk.Button(row_frame, text="Logg", font=body_font, command=lambda f=filename: show_log(os.path.join(folder_path, f)))
    load_log_button.grid(row=0, column=3)


refresh_file_list()

button_frame = tk.Frame(root)
button_frame.grid(row=2, column=2, pady=20, sticky='e')  # Positioned bottom right of file selector

load_article_button = tk.Button(button_frame, text="Load Article", font=body_font, command=load_article_file, bg="#32CD32")
load_article_button.pack(side=tk.LEFT, padx=5)

delete_article_button = tk.Button(button_frame, text="Delete Article", font=body_font, command=delete_file, bg="red")
delete_article_button.pack(side=tk.RIGHT, padx=5)

try:
    # Main logic of your script
    print("run_article.py main logic is running...")

    # (Place your existing code here)

except Exception as e:
    print(f"An error occurred: {e}")


root.mainloop()

