import RPi.GPIO as GPIO
import time

# Constants
PULSES_PER_REVOLUTION = 1000  # Check the encoder spec for correct value
WHEEL_CIRCUMFERENCE_MM = 200  # Set the circumference of the wheel in mm (50 mm diameter wheel)

# GPIO pin definitions
ENCODER_PIN_A = 17
ENCODER_PIN_B = 27

# Variables
last_state_A = GPIO.HIGH  # Track the previous state of ENCODER_PIN_A
current_position = 0

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENCODER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ENCODER_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def calculate_distance_mm(pulses):
    """Calculate distance traveled in mm based on encoder pulses"""
    distance_per_pulse = WHEEL_CIRCUMFERENCE_MM / PULSES_PER_REVOLUTION
    return pulses * distance_per_pulse

try:
    while True:
        # Read the current states of both encoder pins
        current_state_A = GPIO.input(ENCODER_PIN_A)
        current_state_B = GPIO.input(ENCODER_PIN_B)

        # Detect if there's been a state change (i.e., a pulse) on A
        if current_state_A != last_state_A:
            if current_state_A == GPIO.LOW:
                # If A has changed to LOW, check the state of B to determine direction
                if current_state_B == GPIO.LOW:
                    # B is LOW -> forward direction
                    current_position += 1
                else:
                    # B is HIGH -> reverse direction
                    current_position -= 1

            # Update last_state_A to the current state
            last_state_A = current_state_A

            # Calculate and print the distance traveled
            distance_mm = calculate_distance_mm(current_position)
            print(f"Distance traveled: {distance_mm:.2f} mm (Position: {current_position})")

        # Poll every 10 ms (adjust this based on the speed of your encoder)
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Measurement stopped.")

finally:
    GPIO.cleanup()
