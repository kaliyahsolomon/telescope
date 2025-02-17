import RPi.GPIO as GPIO
import time
import math
import threading
from keycheck import kbhit
from star_find import start_process
import smbus2

# Magnetometer parameters
MAGNETOMETER_ADDRESS = 0x1E  # not correct
DATA_REGISTER = 0x03 # not correct

bus = smbus2.SMBus(1)

# Define GPIO pins for ALT motor
DIR_PIN_ALT = 24
STEP_PIN_ALT = 23

# Define GPIO pins for AZ motor
DIR_PIN_AZ = 26 # not correct
STEP_PIN_AZ = 25 # not correct

# Motor parameters
STEPS_PER_REV = 200  # Standard for a 1.8-degree stepper
MICROSTEPPING = 8  # Set according to driver
current_position_alt = 0.0
current_position_az = 0.0
elasped_time = 10

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN_ALT, GPIO.OUT)
GPIO.setup(STEP_PIN_ALT, GPIO.OUT)
GPIO.setup(DIR_PIN_AZ, GPIO.OUT)
GPIO.setup(STEP_PIN_AZ, GPIO.OUT)

def wrap(angle, fullrange):
    return (angle - fullrange) * round(angle/fullrange)

def read_magnetometer():
    """
    Reads the magnetometer to get the current azimuth and altitude.
    """
    data = bus.read_i2c_block_data(MAGNETOMETER_ADDRESS, DATA_REGISTER, 6)
    x = (data[0] << 8) | data[1]
    y = (data[4] << 8) | data[5]
    z = (data[2] << 8) | data[3]

    # Convert to signed 16-bit
    if x > 32767:
        x -= 65536
    if y > 32767:
        y -= 65536
    if z > 32767:
        z -= 65536

    azimuth = math.atan2(y, x) * (180 / math.pi)
    if azimuth < 0:
        azimuth += 360

    magnitude = math.sqrt(x**2 + y**2 + z**2)
    altitude = math.asin(z / magnitude) * (180 / math.pi)

    return azimuth, altitude

def return_to_zero_position(current, dir_pin, step_pin, ):
    """
    Returns the telescope to the zero azimuth and altitude position.
    """
    zero = 0.0
    if dir_pin == DIR_PIN_ALT:
        zero_az, zero_alt = read_magnetometer()  # Get the "zero" azimuth and altitude from the magnetometer
        zero =  zero_alt
    else:
        zero_az, zero_alt = read_magnetometer()  # Get the "zero" azimuth and altitude from the magnetometer
        zero =  zero_az
    # Calculate differences
    diff = current - zero
    

    # Move AZ motor
    if diff != 0:
        direction = "CW" if diff < 0 else "CCW"
        move_stepper(abs(diff), direction, dir_pin, step_pin)

    print("Returned to zero position.")

def first_move(angle, dir_pin, step_pin):
    steps_to_move = int((angle * STEPS_PER_REV * MICROSTEPPING) / 360)
    GPIO.output(dir_pin, GPIO.HIGH)
    for _ in range(steps_to_move):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(0.01)
    

def move_stepper(angle, direction, dir_pin, step_pin):
    steps_to_move = int((angle * STEPS_PER_REV * MICROSTEPPING) / 360)
    step_delay = 1 / (steps_to_move / elasped_time * 2)
    GPIO.output(dir_pin, GPIO.HIGH if direction == "CW" else GPIO.LOW)
    for _ in range(steps_to_move):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(step_delay)

def move(l, current_coord, dir_pin, step_pin):
    first_move(l[0], dir_pin, step_pin)
    current_coord = l[0]
    for i in range(1, len(l)):
        wrap_angle = wrap(current_coord-l[i], 360)
        current_coord = l[i]
        if wrap_angle > 0.0:
            direction = "CW"
            move_stepper(abs(wrap_angle), direction, dir_pin, step_pin)
        elif wrap_angle < 0.0:
            direction = "CCW"
            move_stepper(abs(wrap_angle), direction, dir_pin, step_pin)
        else:
            time.sleep(elasped_time)
        
    return_to_zero_position(current_coord, dir_pin, step_pin)

def move_alt_az(alt, az):
    # Use threading to move ALT and AZ simultaneously
    global current_position_alt, current_position_az
    alt_thread = threading.Thread(target=move, args=(alt, current_position_alt, DIR_PIN_ALT, STEP_PIN_ALT))
    az_thread = threading.Thread(target=move, args=(az, current_position_az, DIR_PIN_AZ, STEP_PIN_AZ))
    
    # Start both threads
    alt_thread.start()
    az_thread.start()
    
    # Wait for both threads to complete
    alt_thread.join()
    az_thread.join()



alt, az = start_process()
move_alt_az(alt, az)
if kbhit():
    print("\nExiting program...")
    alt_thread = threading.Thread(target=return_to_zero_position, args=(current_position_alt, DIR_PIN_ALT, STEP_PIN_ALT))
    az_thread = threading.Thread(target=return_to_zero_position, args=(current_position_az, DIR_PIN_AZ, STEP_PIN_AZ))
    
    # Start both threads
    alt_thread.start()
    az_thread.start()
    
    # Wait for both threads to complete
    alt_thread.join()
    az_thread.join()

    alt, az = start_process()
    move_alt_az(alt, az)

"""

import RPi.GPIO as GPIO
import time
import math

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

l = [0, 0, 0]
current_coord = 0.0

current_coord = l[0]
first_move()
for i in range(1, len(l)):
    if(Math.abs(l[i]-current_coord) > 350):
        "keep w/ current"
    elif(l[i]-current_coord > 0.0):
        "keep w/ current"
    elif(l[i]-current_coord < 0.0):
        "change direction"


def random(angle):
    current_coord = angle
"""