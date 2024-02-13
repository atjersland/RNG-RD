import RPi.GPIO as GPIO
import time
import hashlib
from bitarray import bitarray

#Define constants
GPIO_PIN = 17
TARGET_BITS_PER_FILE = 2048

#Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN)

#Initialize pulse time related variables
step = 1
timestamps = [0, 0, 0, 0]
enough_times = False

pending_bits = bitarray()

#File path for writing binary data
OUTPUT_DIR = "randomBin/"

#Function to be called when the pin goes high
def pin_callback(channel):
    global step, enough_times, timestamps
    
    step += 1
    timestamps[step - 2] = time.time()
    
    if(step == 5):
        enough_times = True
        step = 1

# Add event detection to the pin rising edge
GPIO.add_event_detect(GPIO_PIN, GPIO.RISING, callback=pin_callback)

try:
    while True:
        if(enough_times):
            if(timestamps[1] - timestamps[0] == timestamps[3] - timestamps[2]):
                enough_times = False
                continue
                    
            if(timestamps[1] - timestamps[0] > timestamps[3] - timestamps[2]):
                pending_bits.extend(bitarray('0'))
            else:
                pending_bits.extend(bitarray('1'))
            print(str(len(pending_bits)))
            enough_times = False
            
            if(len(pending_bits) >= TARGET_BITS_PER_FILE):
                file_path = OUTPUT_DIR + hashlib.sha3_256(str(time.time()).encode()).hexdigest() + ".bin"
                with open(file_path, "wb") as file:
                    # Convert bits to bytes
                    pending_bits = pending_bits.tobytes()
                    file.write(pending_bits)
                print(file_path)
                pending_bits = bitarray()

except KeyboardInterrupt:
    # Clean up GPIO on keyboard interrupt
    GPIO.cleanup()