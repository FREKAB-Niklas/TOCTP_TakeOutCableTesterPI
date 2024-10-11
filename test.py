import threading
import time
import RPi.GPIO as GPIO
import os
import tkinter as tk
from tkinter import font, filedialog, messagebox, ttk
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt

# Global variables
measuring = False
current_position = 0
PULSES_PER_REVOLUTION = 600
WHEEL_CIRCUMFERENCE_MM = 200
target_length = 0
distance_label = None
mqtt_broker_ip = "192.168.10.9"
current_segment = 0
allow_motor_run = True
motor_stopped = False  # Initialize motor_stopped for controlling motor state

# Set GPIO mode and pin configurations
GPIO.setmode(GPIO.BCM)  # Set BCM mode at the start
ENCODER_PIN_A = 17
ENCODER_PIN_B = 27
GPIO.setup(ENCODER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENCODER_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Directory and image setup for GUI logo
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "logo.png")

# MQTT setup
client = mqtt.Client()

def connect_mqtt():
    try:
        client.connect(mqtt_broker_ip, 1883, 60)
        client.loop_start()
        print(f"Connected to MQTT broker at {mqtt_broker_ip}")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")

connect_mqtt()

# Calculate distance based on encoder pulses
def calculate_distance_mm(pulses):
    distance_per_pulse = WHEEL_CIRCUMFERENCE_MM / PULSES_PER_REVOLUTION
    return pulses * distance_per_pulse

# Encoder read function to track position
def read_encoder():
    global current_position
    last_state_A = GPIO.input(ENCODER_PIN_A)
    while True:
        current_state_A = GPIO.input(ENCODER_PIN_A)
        current_state_B = GPIO.input(ENCODER_PIN_B)
        
        # Pulse and direction detection
        if current_state_A != last_state_A:
            if current_state_A == GPIO.LOW:
                if current_state_B == GPIO.LOW:
                    current_position += 1
                else:
                    current_position -= 1
            last_state_A = current_state_A
        
        time.sleep(0.001)

# Start encoder reading in a separate thread
encoder_thread = threading.Thread(target=read_encoder, daemon=True)
encoder_thread.start()

# Stop motor function for MQTT control
def stop_motor():
    global motor_stopped
    if not motor_stopped:
        client.publish("motor/control", "stop")
        motor_stopped = True
        print("Sending MQTT message to stop motor")

# Update GUI distance label and handle motor stopping
def update_distance():
    global measuring, motor_stopped
    distance_mm = calculate_distance_mm(current_position)
    distance_label.config(text=f"Kört: {distance_mm:.2f} mm")

    slowdown_threshold = target_length - 50
    if target_length > 0 and distance_mm >= slowdown_threshold and not motor_stopped:
        client.publish("motor/control", "stop")
        print("Sending MQTT message to slow down motor")
        motor_stopped = True

    # Check target length
    if target_length > 0 and distance_mm >= target_length:
        if not motor_stopped:
            stop_motor()
            measuring = False
            reset_counter()
    else:
        if measuring:
            root.after(1000, update_distance)

# Start measuring process
def start_measuring():
    global measuring, motor_stopped
    motor_stopped = False
    measuring = True
    update_distance()

    # Thread to send continuous "run manual" messages
    def send_run_manual():
        while measuring and not motor_stopped:
            client.publish("motor/control", "run manual")
            time.sleep(0.1)

    run_thread = threading.Thread(target=send_run_manual, daemon=True)
    run_thread.start()
    print("Sending continuous 'run manual' commands.")

# Reset encoder counter
def reset_counter():
    global measuring, current_position
    measuring = False
    current_position = 0
    update_distance()

# GUI element for setting target length
def set_target_length():
    global target_length
    try:
        target_length = float(längd_entry.get())
        längd_label.config(text=f"Längd: {target_length} mm")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

# Create a numpad and embed it in the main window
def create_numpad(parent):
    # Updated list of buttons for the numpad
    buttons = [
        '1', '2', '3',
        '4', '5', '6',
        '7', '8', '9',
        '0', 'C', 'OK'  # Replace '.' with 'C' and move 'OK' to the last position
    ]

    # Function to append the value to the entry field
    def append_to_entry(value):
        current_text = längd_entry.get()
        if value == "C":
            längd_entry.delete(0, tk.END)  # Clear the entry field
        elif value == "OK":
            set_target_length()  # Call the set_target_length function when OK is pressed
        else:
            längd_entry.insert(tk.END, value)

    # Create numpad buttons using tk.Button with larger size for touch
    row = 0
    col = 0
    for button in buttons:
        action = lambda x=button: append_to_entry(x)

        # Special colors for 'OK' and 'C'
        if button == "OK":
            tk.Button(parent, text=button, command=action, width=5, height=2, font=("Arial", 24), bd=2, bg="#32CD32", fg="black").grid(row=row, column=col, padx=5, pady=5)
        elif button == "C":
            tk.Button(parent, text=button, command=action, width=5, height=2, font=("Arial", 24), bd=2, bg="red", fg="black").grid(row=row, column=col, padx=5, pady=5)
        else:
            tk.Button(parent, text=button, command=action, width=5, height=2, font=("Arial", 24), bd=2).grid(row=row, column=col, padx=5, pady=5)

        col += 1
        if col > 2:
            col = 0
            row += 1

# Initialize the GUI
root = tk.Tk()
root.title("Ladda Artikel")
root.geometry("800x480")
root.attributes('-fullscreen', True)

# Ensure the window is brought to the front
root.lift()
root.attributes('-topmost', True)
root.after(100, lambda: root.attributes('-topmost', False, '-fullscreen', True))

# Main Frame
main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, sticky='nw')

# Open and resize the image
image = Image.open(logo_path)
scale_percent = 25  # percent of original size
width, height = image.size
new_width = int(width * scale_percent / 100)
new_height = int(height * scale_percent / 100)
resized_image = image.resize((new_width, new_height), Image.LANCZOS)
logo_image = ImageTk.PhotoImage(resized_image)

# Create header frame for the logo
header_frame = tk.Frame(main_frame)
header_frame.grid(row=0, column=0, pady=10, sticky='nw')  # Adjusted to be top left

logo_label = tk.Label(header_frame, image=logo_image)
logo_label.grid(row=0, column=0, padx=10, pady=0)

# Entry field for "Längd" with label
längd_label = ttk.Label(main_frame, text="Längd: 0 mm", font=("Arial", 20))
längd_label.grid(row=1, column=0, pady=10)

längd_entry = ttk.Entry(main_frame, font=("Arial", 20))
längd_entry.grid(row=2, column=0, pady=10)

# Define and assign distance_label
distance_label = ttk.Label(main_frame, text="Kört: 0 mm", font=("Arial", 24))
distance_label.grid(row=3, column=0, pady=20)

# Create Start and Reset buttons side by side with proper centering
button_frame = tk.Frame(main_frame)
button_frame.grid(row=5, column=0, columnspan=2, pady=10)

start_button = tk.Button(button_frame, text="Start", command=start_measuring, width=10, height=5, font=("Arial", 16), bd=2, bg="#32CD32", fg="black")
start_button.grid(row=0, column=0, padx=5)

reset_button = tk.Button(button_frame, text="Reset", command=reset_counter, width=10, height=5, font=("Arial", 16), bd=2, bg="yellow", fg="black")
reset_button.grid(row=0, column=1, padx=5)

# Frame for Numpad (placed to the right)
numpad_frame = tk.Frame(root)
numpad_frame.grid(row=0, column=1, padx=50, pady=50, sticky='n')  # Adjust position as needed

# Create the numpad in the main window
create_numpad(numpad_frame)

# Update the distance label every second
update_distance()

# Start the Tkinter event loop
root.mainloop()

# Cleanup GPIO on exit
GPIO.cleanup()
