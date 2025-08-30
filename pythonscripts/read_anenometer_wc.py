import serial
import time
import os
import csv 
import sys
import argparse

parser = argparse.ArgumentParser(description='Log anemometer data with position and duty cycle.')
parser.add_argument('--span', type=float, required=True, help='Spanwise position in ft')
parser.add_argument('--dl', type=float, required=True, help='downstream location in ft')
parser.add_argument('--dutycycle', type=int, required=True, help='Wind tunnel duty cycle percentage')

args = parser.parse_args()
# Format span and dl to string with decimals, then replace '.' with '_'
span_str = str(args.span).replace('.', '_')
dl_str = str(args.dl).replace('.', '_')

ser = serial.Serial(
    port='COM5',      
    baudrate=115200,      
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

time.sleep(2)

base_path = 'C:\\AWARELab\\anemometer_data'
csv_filename = f"{base_path}_dl{dl_str}_span{span_str}_dc{int(args.dutycycle)}.csv"
#csv_filename = 'C:\\AWARELab\\anemometer_data.csv'

csv_file = open(csv_filename, mode='w', newline='')
csv_writer = csv.writer(csv_file)
print("CSV absolute path:", os.path.abspath(csv_filename))

timespan = 30 #seconds
start_time = time.time()
cur_time = time.time()
count = 0
s_sum = 0
variance = 0
speeds = []

try:
    while cur_time <= start_time + timespan:
        raw_line = ser.read_until()  
        line = raw_line.decode('ascii', errors='ignore').strip()
        if not line:
            continue

        print(f"Received: {line}")

        #ts = time.strftime('%Y-%m-%d %H:%M:%S')
        
        #csv_writer.writerow([ts, line.split()])
        row = line.split()
        s_sum += float(row[1])
        csv_writer.writerow(row)
        csv_file.flush()
        cur_time = time.time()
        count+=1

except KeyboardInterrupt:
    print("Stopping serial read.")

finally:
    avg = float(s_sum/count)
    print("Average Speed: " + str(s_sum/count))
    for s in speeds:
        variance += math.pow(s - avg, 2)
    stddev = math.sqrt(variance/count)
    print("Standard Deviation:", str(stddev))
    print ("Turbulence Intensity: ", str(stddev/avg))
    print("Readings: " + str(count))
    print("Time Elapsed: " + str(cur_time-start_time))
    print("Frequency: " + str(count/(cur_time-start_time)))
    csv_file.close()
    ser.close()
    print("CSV file and serial port closed.")