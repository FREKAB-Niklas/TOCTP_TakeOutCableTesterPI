import pigpio

pi = pigpio.pi()

if not pi.connected:
    print("Failed to connect to pigpio daemon")
    exit()

test_pins = [17, 27, 22]

for pin in test_pins:
    pi.set_mode(pin, pigpio.OUTPUT)
    print(f"Pin {pin} set up as OUTPUT.")

    pi.write(pin, 1)
    print(f"Pin {pin} set to HIGH (ON).")
    
    pi.write(pin, 0)
    print(f"Pin {pin} set to LOW (OFF).")

pi.stop()
