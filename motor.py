import RPi.GPIO as GPIO
import time

# Define GPIO pins
DIR_PIN = 24    # Direction pin
STEP_PIN = 23   # Step pin

# Motor parameters
STEPS_PER_REV = 200  # Standard for a 1.8-degree stepper
MICROSTEPPING = 8   # Set according to driver (1, 2, 4, 8, 16, etc.)
TOTAL_STEPS = 0

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

# Set microstepping mode (example: 1/16 microstep mode for A4988/DRV8825)
def move_stepper(angle, direction):
    """
    Moves the stepper motor to the specified angle.
    :param angle: The angle in degrees to move.
    :param direction: "CW" for clockwise, "CCW" for counterclockwise.
    """
    steps_to_move = int((angle/360) * (STEPS_PER_REV * MICROSTEPPING))


    # Set direction
    GPIO.output(DIR_PIN, GPIO.HIGH if direction == "CW" else GPIO.LOW)

    for _ in range(steps_to_move):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)  # Pulse width (adjust for speed)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.001)
        TOTAL_STEPS = TOTAL_STEPS + 1

try:
    while True:
        angle = float(input("Enter angle (0-360): "))
        direction = input("Enter direction (CW/CCW): ").strip().upper()
        if direction in ["CW", "CCW"]:
            move_stepper(angle, direction)
        else:
            print("Invalid direction. Use 'CW' or 'CCW'.")

except KeyboardInterrupt:
    print("\nExiting program.")
    if direction == "CW":
        move_stepper(TOTAL_STEPS, "CCW")
    else:
        move_stepper(angle, "CW")
    GPIO.cleanup()