import RPi.GPIO as GPIO
import time
import math
import threading

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
elasped_time = 1

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN_ALT, GPIO.OUT)
GPIO.setup(STEP_PIN_ALT, GPIO.OUT)
GPIO.setup(DIR_PIN_AZ, GPIO.OUT)
GPIO.setup(STEP_PIN_AZ, GPIO.OUT)

def wrap(angle, fullrange):
    return (angle - fullrange) * round(angle/fullrange)

def move(current_coord, desired_coord, dir_pin, step_pin):
        wrap_angle = wrap(current_coord-desired_coord, 360)

        if wrap_angle > 0.0:
            direction = "CW"
            move_stepper(abs(wrap_angle), direction, dir_pin, step_pin)
        elif wrap_angle < 0.0:
            direction = "CCW"
            move_stepper(abs(wrap_angle), direction, dir_pin, step_pin)
        
        

def move_alt_az(curr_alt, curr_az, des_alt, des_az):
    alt_thread = threading.Thread(target=move, args=(curr_alt, des_alt, DIR_PIN_ALT, STEP_PIN_ALT))
    az_thread = threading.Thread(target=move, args=(curr_alt, des_alt, DIR_PIN_AZ, STEP_PIN_AZ))
    
    # Start both threads
    alt_thread.start()
    az_thread.start()
    
    # Wait for both threads to complete
    alt_thread.join()
    az_thread.join()

def move_stepper(angle, direction, dir_pin, step_pin):
    steps_to_move = int((angle * STEPS_PER_REV * MICROSTEPPING) / 360)
    step_delay = 1 / (steps_to_move / elasped_time * 2)
    GPIO.output(dir_pin, GPIO.HIGH if direction == "CW" else GPIO.LOW)
    for _ in range(steps_to_move):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(step_delay)

while True:
        curr_alt = float(input("Enter your current altitude angle (0-360): "))
        curr_az = float(input("Enter your current azimuth angle (0-360): "))
        des_alt = float(input("Enter your desired altitude angle (0-360): "))
        des_az = float(input("Enter your desired azimuth angle (0-360): "))
        move_alt_az(curr_alt, curr_az, des_alt, des_az)
        
