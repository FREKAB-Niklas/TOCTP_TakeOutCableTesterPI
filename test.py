import threading
import time
import RPi.GPIO as GPIO
import os
import tkinter as tk
from tkinter import font, filedialog, messagebox, ttk
from PIL import Image, ImageTk

# Global variables
measuring = False
current_position = 0
PULSES_PER_REVOLUTION = 2400
WHEEL_CIRCUMFERENCE_MM = 200
target_length = 0  # Target length from the "Längd" input

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "logo.png")

# GPIO setup for the encoder
ENCODER_PIN_A = 17
ENCODER_PIN_B = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENCODER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENCODER_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to calculate distance
def calculate_distance_mm(pulses):
    distance_per_pulse = WHEEL_CIRCUMFERENCE_MM / PULSES_PER_REVOLUTION
    return pulses * distance_per_pulse

# Encoder reading function
def read_encoder():
    global current_position, measuring
    last_state_A = GPIO.input(ENCODER_PIN_A)
    while measuring:
        current_state_A = GPIO.input(ENCODER_PIN_A)
        current_state_B = GPIO.input(ENCODER_PIN_B)
        
        # Detect pulse and direction
        if current_state_A != last_state_A:
            if current_state_A == GPIO.LOW:
                if current_state_B == GPIO.LOW:
                    current_position += 1
                else:
                    current_position -= 1
            last_state_A = current_state_A
        
        time.sleep(0.001)

# Start measuring function
def start_measuring():
    global measuring
    measuring = True
    thread = threading.Thread(target=read_encoder)
    thread.start()

# Reset the counter and stop measuring
def reset_counter():
    global measuring, current_position
    measuring = False
    current_position = 0
    update_distance()

# Function to update distance on the GUI
def update_distance():
    distance_mm = calculate_distance_mm(current_position)
    root.distance_label.config(text=f"Kört: {distance_mm:.2f} mm")
    if target_length > 0 and distance_mm >= target_length:
        messagebox.showinfo("Done", "Target length reached!")
        reset_counter()  # Auto-reset after reaching the target length
    root.after(1000, update_distance)  # Update every second

# Function to set the target length from entry
def set_target_length():
    global target_length
    try:
        target_length = float(längd_entry.get())  # Convert input to a float
        längd_label.config(text=f"Längd: {target_length} mm")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

# Create a simple numpad to input numbers
def open_numpad():
    numpad = tk.Toplevel(root)
    numpad.title("Numpad")
    numpad.geometry("400x600")  # Larger size for the small display

    # List of buttons for the numpad
    buttons = [
        '1', '2', '3',
        '4', '5', '6',
        '7', '8', '9',
        '0', '.', 'C'
    ]

    # Function to append the value to the entry field
    def append_to_entry(value):
        current_text = längd_entry.get()
        if value == "C":
            längd_entry.delete(0, tk.END)  # Clear the entry field
        else:
            längd_entry.insert(tk.END, value)

    # Create numpad buttons using tk.Button with larger size
    row = 0
    col = 0
    for button in buttons:
        action = lambda x=button: append_to_entry(x)
        tk.Button(numpad, text=button, command=action, width=10, height=4).grid(row=row, column=col, padx=5, pady=5)
        col += 1
        if col > 2:
            col = 0
            row += 1

    # Confirm button
    tk.Button(numpad, text="OK", command=lambda: (set_target_length(), numpad.destroy()), width=10, height=4).grid(row=row+1, column=0, columnspan=3, pady=10)


# Initialize the GUI
root = tk.Tk()
root.title("Ladda Artikel")
root.geometry("800x480")
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.destroy())  # Allow exiting fullscreen with the Esc key

# Ensure the window is brought to the front
root.lift()
root.attributes('-topmost', True)
root.after(100, lambda: root.attributes('-topmost', False, '-fullscreen', True))

# Open and resize the image
image = Image.open(logo_path)
scale_percent = 50  # percent of original size
width, height = image.size
new_width = int(width * scale_percent / 100)
new_height = int(height * scale_percent / 100)
resized_image = image.resize((new_width, new_height), Image.LANCZOS)
logo_image = ImageTk.PhotoImage(resized_image)

# Create header frame for the logo
header_frame = tk.Frame(root)
header_frame.grid(row=0, column=0, pady=10, sticky='nw')  # Adjusted to be top left

logo_label = tk.Label(header_frame, image=logo_image)
logo_label.grid(row=0, column=0, padx=10, pady=0)
logo_label.bind("<Button-1>", lambda e: root.destroy())

# Entry field for "Längd" with label
längd_label = ttk.Label(root, text="Längd: 0 mm", font=("Arial", 20))
längd_label.grid(row=1, column=0, pady=10)

längd_entry = ttk.Entry(root, font=("Arial", 20))
längd_entry.grid(row=2, column=0, pady=10)
längd_entry.bind("<FocusIn>", lambda e: open_numpad())  # Show numpad on focus

# Create Start button using grid
start_button = ttk.Button(root, text="Start", command=start_measuring)
start_button.grid(row=3, column=0, pady=10)

# Create Reset button using grid
reset_button = ttk.Button(root, text="Reset", command=reset_counter)
reset_button.grid(row=4, column=0, pady=10)

# Label to show the distance as "Kört"
root.distance_label = ttk.Label(root, text="Kört: 0 mm", font=("Arial", 24))
root.distance_label.grid(row=5, column=0, pady=20)

# Update the distance label every second
update_distance()

# Start the Tkinter event loop
root.mainloop()

# Cleanup GPIO on exit
GPIO.cleanup()
