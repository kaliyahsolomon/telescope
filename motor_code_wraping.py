import RPi.GPIO as GPIO
import time
import math
from keycheck import kbhit
from star_find import start_process()
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

def first_move(angle, dir_pin, step_pin):
    """
    Moves the stepper motor to an initial position.
    """
    direction = "CW"
    steps_to_move = int((angle * STEPS_PER_REV * MICROSTEPPING) / 360)
    GPIO.output(dir_pin, GPIO.HIGH if direction == "CW" else GPIO.LOW)

    for _ in range(steps_to_move):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(0.01)  # Pulse width (adjust for speed)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(0.01)

    print("Finished first move")

def return_to_zero_position(current_az, current_alt, dir_pin_az, step_pin_az, dir_pin_alt, step_pin_alt):
    """
    Returns the telescope to the zero azimuth and altitude position.
    """
    zero_az, zero_alt = read_magnetometer()  # Get the "zero" azimuth and altitude from the magnetometer

    # Calculate differences
    az_diff = current_az - zero_az
    alt_diff = current_alt - zero_alt

    # Move AZ motor
    if az_diff != 0:
        direction_az = "CW" if az_diff < 0 else "CCW"
        move_stepper(abs(az_diff), direction_az, current_position_az, dir_pin_az, step_pin_az)

    # Move ALT motor
    if alt_diff != 0:
        direction_alt = "CW" if alt_diff < 0 else "CCW"
        move_stepper(abs(alt_diff), direction_alt, current_position_alt, dir_pin_alt, step_pin_alt)

    print("Returned to zero position.")

def move_stepper(direction_az, direction_alt, angle_az, angle_alt, dir_pin_az, step_pin_az, dir_pin_alt, step_pin_alt):
    """
    Moves the stepper motor to the specified angle.
    """
    steps_to_move_az = int((angle_az * STEPS_PER_REV * MICROSTEPPING) / 360)
    step_delay_az = 1 / (steps_to_move_az / (elasped_time) * 2)
    steps_to_move_alt = int((angle_alt * STEPS_PER_REV * MICROSTEPPING) / 360)
    step_delay_alt = 1 / (steps_to_move_alt / (elasped_time) * 2)

    GPIO.output(dir_pin_az, GPIO.HIGH if direction_az == "CW" else GPIO.LOW)
    GPIO.output(dir_pin_alt, GPIO.HIGH if direction_alt == "CW" else GPIO.LOW)

    for i in range(steps_to_move):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(step_delay)

    print(f"Moved to angle:")

def move(alt_list, az_list, dir_pin_az, step_pin_az, dir_pin_alt, step_pin_alt):
    current_position_alt = alt_list[0]
    current_position_az = az_list[0]
    first_move(alt_list[0], az_list[0], dir_pin_az, step_pin_az, dir_pin_alt, step_pin_alt)

    for i in range(1, len(alt_list)):
        wrap_angle_alt = wrap(current_position_alt-alt_list[i], 360)
        wrap_angle_az = wrap(current_position_az-az_list[i], 360)
        current_position_alt = alt_list[i]
        current_position_az = az_list[i]
        direction_alt
        direction_az
        if wrap_angle_az > 0.0:
            direction_az = "CW"
        elif wrap_angle_az < 0.0:
            direction_az = "CCW"
        elif wrap_angle_az == 0.0:
            direction_az = "CW"
        if wrap_angle_alt > 0.0:
            direction_alt = "CW"
        elif wrap_angle_alt < 0.0:
            direction_alt = "CCW"
        elif wrap_angle_alt == 0.0:
            direction_alt = "CW"
        move_stepper(direction_az, direction_alt, abs(wrap_angle_az), abs(wrap_angle_alt), dir_pin_az, step_pin_az, dir_pin_alt, step_pin_alt)
        

    print("Returning to origin...")
    return_to_zero_position(current_position_az, current_position_alt, DIR_PIN_AZ, STEP_PIN_AZ, DIR_PIN_ALT, STEP_PIN_ALT)
    print("Returned to origin")

alt, az = start_process()
move(alt, current_position_alt, DIR_PIN_ALT, STEP_PIN_ALT)
move(az, current_position_az, DIR_PIN_AZ, STEP_PIN_AZ)

if kbhit():
    print("\nExiting program.")
    print("Returning to origin...")
    return_to_zero_position(current_position_az, current_position_alt, DIR_PIN_AZ, STEP_PIN_AZ, DIR_PIN_ALT, STEP_PIN_ALT)
    print("Returned to origin")

    alt, az = start_process()
    move(alt, current_position_alt, DIR_PIN_ALT, STEP_PIN_ALT)
    move(az, current_position_az, DIR_PIN_AZ, STEP_PIN_AZ)
