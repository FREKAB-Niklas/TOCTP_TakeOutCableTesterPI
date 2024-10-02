import tkinter as tk
from tkinter import ttk
import threading
import time
import RPi.GPIO as GPIO

# Global variables
measuring = False
current_position = 0
PULSES_PER_REVOLUTION = 2400
WHEEL_CIRCUMFERENCE_MM = 200

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

# GUI Application
class EncoderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Encoder Distance Measurement")
        self.geometry("480x320")  # Match the touchscreen size

        # Ensure the window is brought to the front
        self.lift()
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False, '-fullscreen', True))

        
        # Create Start button
        self.start_button = ttk.Button(self, text="Start", command=start_measuring)
        self.start_button.pack(pady=10)
        
        # Create Stop button
        self.stop_button = ttk.Button(self, text="Stop", command=stop_measuring)
        self.stop_button.pack(pady=10)
        
        # Label to show the distance
        self.distance_label = ttk.Label(self, text="Distance: 0 mm", font=("Arial", 24))
        self.distance_label.pack(pady=20)
        
        # Update the distance label every second
        self.update_distance()
    
    def update_distance(self):
        distance_mm = calculate_distance_mm(current_position)
        self.distance_label.config(text=f"Distance: {distance_mm:.2f} mm")
        self.after(1000, self.update_distance)  # Update every second

# Initialize and run the application
if __name__ == "__main__":
    app = EncoderApp()
    app.mainloop()

    # Cleanup GPIO on exit
    GPIO.cleanup()
