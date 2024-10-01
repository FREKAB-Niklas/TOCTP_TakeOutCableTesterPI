import RPi.GPIO as GPIO
import time

# Constants
PULSES_PER_REVOLUTION = 1000  # Check the encoder spec for correct value
WHEEL_CIRCUMFERENCE_MM = 200  # Set the circumference of the wheel in mm (50 mm diameter wheel)

# GPIO pin definitions
ENCODER_PIN_A = 17
ENCODER_PIN_B = 27  # Add a second pin if you're using quadrature encoding, otherwise leave it out

# Variables
last_state_A = GPIO.HIGH  # Track the previous state of ENCODER_PIN_A
current_position = 0

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENCODER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENCODER_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Only if you have a B pin

def calculate_distance_mm(pulses):
    """Calculate distance traveled in mm based on encoder pulses"""
    distance_per_pulse = WHEEL_CIRCUMFERENCE_MM / PULSES_PER_REVOLUTION
    return pulses * distance_per_pulse

try:
    while True:
        # Read the current state of the encoder pin A
        current_state_A = GPIO.input(ENCODER_PIN_A)
        
        # Detect if there's been a state change (i.e., a pulse)
        if current_state_A != last_state_A:
            if current_state_A == GPIO.LOW:
                # If the pin went from HIGH to LOW, it indicates a pulse
                current_position += 1  # Increment the pulse count

            # Update last_state_A to the current state
            last_state_A = current_state_A

            # Calculate and print the distance traveled
            distance_mm = calculate_distance_mm(current_position)
            print(f"Distance traveled: {distance_mm:.2f} mm")

        # Poll every 10 ms (adjust this based on the speed of your encoder)
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Measurement stopped.")

finally:
    GPIO.cleanup()
