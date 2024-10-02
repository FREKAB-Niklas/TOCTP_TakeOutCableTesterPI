import threading
import time
import RPi.GPIO as GPIO
import os
import sys
import tkinter as tk
from tkinter import font, filedialog, messagebox, ttk
from PIL import Image, ImageTk

# Global variables
measuring = False
current_position = 0
PULSES_PER_REVOLUTION = 2400
WHEEL_CIRCUMFERENCE_MM = 200

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the image file inside the PI folder
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

# Stop measuring function
def stop_measuring():
    global measuring
    measuring = False

# Function to update distance on the GUI
def update_distance():
    distance_mm = calculate_distance_mm(current_position)
    root.distance_label.config(text=f"Distance: {distance_mm:.2f} mm")
    root.after(1000, update_distance)  # Update every second

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
logo_label.pack(side=tk.LEFT, padx=10, pady=0)
logo_label.bind("<Button-1>", lambda e: root.destroy())

# Create Start button
start_button = ttk.Button(root, text="Start", command=start_measuring)
start_button.pack(pady=10)

# Create Stop button
stop_button = ttk.Button(root, text="Stop", command=stop_measuring)
stop_button.pack(pady=10)

# Label to show the distance
root.distance_label = ttk.Label(root, text="Distance: 0 mm", font=("Arial", 24))
root.distance_label.pack(pady=20)

# Update the distance label every second
update_distance()

# Start the Tkinter event loop
root.mainloop()

# Cleanup GPIO on exit
GPIO.cleanup()
