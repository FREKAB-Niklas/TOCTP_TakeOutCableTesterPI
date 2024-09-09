import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
import os
import paho.mqtt.client as mqtt

# MQTT setup (assuming same setup as in run_article.py)
mqtt_broker_ip = "192.168.10.9"
client = mqtt.Client()
client.connect(mqtt_broker_ip, 1883, 60)

# Global variables
calculated = False
total_rotations = 0
current_stop = 0
rotations_per_stop = 0

# Constants
CABLE_DIAMETER = 8.0  # in mm

def calculate_rotations():
    global calculated, total_rotations, rotations_per_stop, current_stop
    try:
        length = float(length_entry.get())
        spacing = float(spacing_entry.get())
        stops = int(stops_entry.get())

        if stops < 1:
            raise ValueError("Stops must be at least 1")

        total_rotations = (length * 1000) / (math.pi * CABLE_DIAMETER)
        rotations_per_stop = (spacing * 1000) / (math.pi * CABLE_DIAMETER)

        calculated = True
        current_stop = 0
        update_motor_button()
        messagebox.showinfo("Calculation Complete", f"Total rotations: {total_rotations:.2f}\nRotations per stop: {rotations_per_stop:.2f}")
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))

def run_motor():
    global current_stop
    if not calculated:
        messagebox.showerror("Error", "Please calculate rotations first")
        return

    if current_stop < int(stops_entry.get()):
        client.publish("motor/control", str(rotations_per_stop))
        current_stop += 1
        update_motor_button()
        messagebox.showinfo("Motor Run", f"Motor ran for stop {current_stop}")
    else:
        messagebox.showinfo("Complete", "All stops completed")
        calculated = False
        update_motor_button()

def update_motor_button():
    if calculated and current_stop < int(stops_entry.get()):
        motor_button.config(bg="green", state=tk.NORMAL)
    else:
        motor_button.config(bg="gray", state=tk.DISABLED)

# Create main window
root = tk.Tk()
root.title("Manual Motor Control")
root.geometry("1920x1080")
root.attributes('-fullscreen', True)

# Fonts
header_font = font.Font(family="Helvetica", size=24, weight="bold")
body_font = font.Font(family="Helvetica", size=16)

# Header
header_frame = tk.Frame(root)
header_frame.pack(side=tk.TOP, fill=tk.X)

# Logo (assuming same logo as in run_article.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "logo.png")
image = Image.open(logo_path)
scale_percent = 50
width, height = image.size
new_width = int(width * scale_percent / 100)
new_height = int(height * scale_percent / 100)
resized_image = image.resize((new_width, new_height), Image.LANCZOS)
logo_image = ImageTk.PhotoImage(resized_image)

logo_label = tk.Label(header_frame, image=logo_image)
logo_label.pack(side=tk.LEFT, padx=10, pady=10)

title_label = tk.Label(header_frame, text="Manual Motor Control", font=header_font)
title_label.pack(side=tk.LEFT, padx=10, pady=10)

# Main content
content_frame = tk.Frame(root)
content_frame.pack(expand=True, padx=20, pady=20)

# Entry fields
tk.Label(content_frame, text="Length (m):", font=body_font).grid(row=0, column=0, sticky="e", pady=5)
length_entry = tk.Entry(content_frame, font=body_font)
length_entry.grid(row=0, column=1, pady=5)

tk.Label(content_frame, text="Spacing (m):", font=body_font).grid(row=1, column=0, sticky="e", pady=5)
spacing_entry = tk.Entry(content_frame, font=body_font)
spacing_entry.grid(row=1, column=1, pady=5)

tk.Label(content_frame, text="Stops:", font=body_font).grid(row=2, column=0, sticky="e", pady=5)
stops_entry = tk.Entry(content_frame, font=body_font)
stops_entry.grid(row=2, column=1, pady=5)

# Buttons
button_frame = tk.Frame(content_frame)
button_frame.grid(row=3, column=0, columnspan=2, pady=20)

calculate_button = tk.Button(button_frame, text="Calculate", font=body_font, command=calculate_rotations, bg="#0A60C5", fg="white", width=15, height=2)
calculate_button.pack(side=tk.LEFT, padx=10)

motor_button = tk.Button(button_frame, text="Run Motor", font=body_font, command=run_motor, bg="gray", width=15, height=2)
motor_button.pack(side=tk.LEFT, padx=10)
motor_button.config(state=tk.DISABLED)

# Exit button
exit_button = tk.Button(root, text="Exit", font=body_font, command=root.destroy, bg="red", fg="white")
exit_button.pack(side=tk.BOTTOM, pady=10)

root.mainloop()
