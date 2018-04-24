import socket
import sys
import time
from ina219 import INA219
from ina219 import DeviceRangeError
from collections import deque
import pigpio
import xlsxwriter
import threading
import RPi.GPIO as GPIO
import os
import logging
import random
import numpy as np
import matplotlib.pyplot as plt
from Adafruit_BNO055 import BNO055
os.system('sudo pigpiod')
time.sleep(1)


#-----------TCP Connectivity-----------------
TCP_IP = ''
TCP_PORT = 50007
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Server socket is created')
try:
    s.bind((TCP_IP, TCP_PORT))
except:
    print('Error: No binding could be done')
    sys.exit()

s.listen(0)
print('Socket is now listening')

conn,addr = s.accept()
print('Connection address:', addr)

message = 'Data received'
messageBytes = message.encode('utf-8')

data = conn.recv(BUFFER_SIZE)         
ReceivedData = str(data.decode('utf-8'))
print('Received data: ', ReceivedData)
conn.sendall(messageBytes) #echo
time.sleep(1)
#--------------------------------------------------


#-----------ESC Configuration----------------------
ESC1 = 4 # Motor1
ESC2 = 17 # Motor2
ESC3 = 24 # Rudders
ESC4 = 25 # Sails



pi = pigpio.pi()

STBY = 23
AIN2 = 21 # For motor direction
AIN1 = 20 # For motor direction
BIN1 = 27 # For motor direction
BIN2 = 22 # For motor direction

pi.set_mode(STBY, pigpio.OUTPUT) # Setting GPIO 23 as OUTPUT
pi.set_mode(AIN1, pigpio.OUTPUT)
pi.set_mode(AIN2, pigpio.OUTPUT)
pi.set_mode(BIN1, pigpio.OUTPUT)
pi.set_mode(BIN2, pigpio.OUTPUT)
pi.write(STBY,1) # Turining GPIO 23 High

heading = 0 # initial heading angle zero
PWM1 = 0 # PWM for Motor1
PWM2 = 0 # PWM for Motor2
#---------------------------------------------

flag = False
#-------------Receiving Commands-----------------
def looping():
    
    global flag
    global PWM1
    global PWM2
    flag = False
    angle = 1300 # Rudder Straight
    while True:
        data = conn.recv(BUFFER_SIZE)
        
        ReceivedData = str(data.decode('utf-8'))
        
        if ReceivedData.upper() == "C":
            flag = True
            break
        elif ReceivedData.upper() == "W":
            print('Moving Forward')
            pi.set_servo_pulsewidth(ESC3,angle)
            pi.set_servo_pulsewidth(ESC4,900) # Sails Tighten
            pi.write(AIN1,1) # Turining GPIO 20 Low
            pi.write(AIN2,0) # Turining GPIO 21 High
            pi.write(BIN1,1) # Turining GPIO 27 Low
            pi.write(BIN2,0) # Turining GPIO 22 High
            PWM1 = 255
            PWM2 = 200
        elif  ReceivedData.upper() == "S":
            print('Stopped')
            PWM1 = 0
            PWM2 = 0
            pi.set_servo_pulsewidth(ESC3,angle)
            pi.set_servo_pulsewidth(ESC4,900)
        elif  ReceivedData.upper() == "A":
            print('Turning Left')
            pi.set_servo_pulsewidth(ESC3,800)
            pi.set_servo_pulsewidth(ESC4,1700) # Sails Loosen
            pi.write(AIN1,1) # Turining GPIO 20 Low
            pi.write(AIN2,0) # Turining GPIO 21 High
            pi.write(BIN1,0) # Turining GPIO 27 Low
            pi.write(BIN2,1) # Turining GPIO 22 High
            PWM1 = 255
            PWM2 = 220
        elif  ReceivedData.upper() == "D":
            print('Turning Right')
            pi.set_servo_pulsewidth(ESC4,1700) # Sails Loosen
            pi.set_servo_pulsewidth(ESC3,1700)
            pi.write(AIN1,0) # Turining GPIO 20 Low
            pi.write(AIN2,1) # Turining GPIO 21 High
            pi.write(BIN1,1) # Turining GPIO 27 Low
            pi.write(BIN2,0) # Turining GPIO 22 High
            PWM1 = 220
            PWM2 = 255
        else:
            PWM1 = 0
            PWM2 = 0
            pi.set_servo_pulsewidth(ESC3,angle) # Rudder Straight
            pi.set_servo_pulsewidth(ESC4,900) # Sails Tighten

        pi.set_PWM_dutycycle(ESC1, PWM1)
        pi.set_PWM_dutycycle(ESC2, PWM2)
        time.sleep(0.5)
            
    pi.set_PWM_dutycycle(ESC1, 0)
    pi.set_PWM_dutycycle(ESC2, 0)
    pi.set_servo_pulsewidth(ESC3,angle) # Rudder Straight
    pi.set_servo_pulsewidth(ESC4,900) # Sails Tighten
    print('Motors Stopped \n')
    time.sleep(0.4)
    pi.stop()
    time.sleep(0.5)

    
#    conn.close()
#    time.sleep(1)
#    print('Connection closed!')

#------------------------------------------------

def IMU():

    global heading
    
    try:
        # Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
        bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

        # Enable verbose debug logging if -v is passed as a parameter.
        if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
            logging.basicConfig(level=logging.DEBUG)

        # Initialize the BNO055 and stop if something went wrong.
        if not bno.begin():
            raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

        # Print system status and self test result.
        status, self_test, error = bno.get_system_status()
        print('System status: {0}'.format(status))
        print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
        # Print out an error if system status is in error mode.
        if status == 0x01:
            print('System error: {0}'.format(error))
            print('See datasheet section 4.3.59 for the meaning.')

        # Print BNO055 software revision and other diagnostic data.
#        sw, bl, accel, mag, gyro = bno.get_revision()
#        print('Software version:   {0}'.format(sw))
#        print('Bootloader version: {0}'.format(bl))
#        print('Accelerometer ID:   0x{0:02X}'.format(accel))
#        print('Magnetometer ID:    0x{0:02X}'.format(mag))
#        print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))


        print('Reading BNO055 data, press Ctrl-C to quit...')
        stime = np.array([])
        sHeading = np.array([])
        #CalibData = bno.get_calibration()
        CalibData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 232, 3, 0, 0] #Sensor Calibration data
        bno.set_calibration(CalibData) # Sensor Calibration

        # Print system calibration status
        system, gyr, accellro, magno = bno.get_calibration_status()
#        print('System Calibration Status = ',int(system)) # 0 for no calibration, and 3 for maximum calibration
#        print('Gyro Calibration Status = ',int(gyr))
#        print('Accelerometer Calibration Status = ', int(accellro))
#        print('Magnetometer Calibration Status = ', int(magno))

        try:
            
            
            while True:

                if flag:
                    break # End the loop when flag turned True
                
                # Read the Euler angles for heading, roll, pitch (all in degrees).
                heading, roll, pitch = bno.read_euler()
                
                # Print everything out.
                print('Heading={0:0.2F}'.format(heading))
                
                #newTime = time.clock()
                #stime = np.append(stime,newTime)
                #sHeading = np.append(sHeading,heading)
                time.sleep(0.5)
                

        except:
            print('An exception occured \n')
    except:
        print('An error occured \n')


    print('IMU Loop Ended \n')

#------------------------------------------------

def Sensor():
    
    Shunt_OHMS = 0.1 # For this sensor it is 0.1 ohm

    try:
        print('Starting Current Sensor')
        print('Collecting Sensor Values...')
        start = time.time() # Start Time
        
        #global DataPoints
        DataPoints = deque(maxlen=None) # Creating Array of datatype Deque to store values

        a = 0.9664 # Regression Fitting Parameter
        b = 0.0285 # Regression Fitting Parameter

        ina = INA219(Shunt_OHMS) # Auto Gain
            
        ina.configure()
        print('Current Sensor Configured Successfully')
        while True:            
            
            if flag:
                #print('Breaking loop')
                # Break when flag = True
                break
        
            
            #print('Bus Voltage: %.3f V' % ina.voltage())

            try:
                #print('Bus Current: %.3f mA' % ina.current())
                #print('Power: %.3f mW' % ina.power())
                currentvalue = round((a*ina.current())+b) # Rounding off values to nearest integer
                voltagevalue = float('{0:.1f}'.format(ina.voltage())) # Floating point up to one decimal point
                powervalue = round(currentvalue*voltagevalue)
                timevalue = float('{0:.1f}'.format(time.time()-start)) # Elapsed time in Seconds with 1 decimal point floating number 
                headingvalue = float('{0:.2f}'.format(heading))
                DataPoints.append([timevalue, currentvalue, voltagevalue, powervalue, PWM1, PWM2, headingvalue]) # Updating DataPoints Array

            except DeviceRangeError:
                print('Device Range Error')

            time.sleep(0.5) # Reading value after 0.5 second
        
    except:        
        print('Exception Occurred, Current Sensor Stopped \n')

    
    Wt = input('Do you want to store the sensor values Y/N? ')

    if Wt == 'y':
        writing(DataPoints)
    else:
        print('Ending without saving sensor data \n')

    print('Sensor Stopped!\n')
#------------------------------------------------

def writing(Data):

    rnd = random.randint(1,100)
    runDate = time.ctime() 
    workbook = xlsxwriter.Workbook('SensorValues(%d).xlsx'%rnd,{'constant_memory': True})  # Creating XLSX File for Data Keeping 
    worksheet = workbook.add_worksheet() # Generating worksheet

    bold = workbook.add_format({'bold':True}) # Formating for Bold text

    worksheet.write('A1', 'Time', bold) # Writing Column Titles
    worksheet.write('B1', 'Current (mA)', bold)
    worksheet.write('C1', 'Voltage (v)', bold)
    worksheet.write('D1', 'Power (mW)', bold)
    worksheet.write('E1', 'PWM1', bold)
    worksheet.write('F1', 'PWM2', bold)
    worksheet.write('G1', 'Heading Angle', bold)
    worksheet.write('H1', 'Start Time', bold)
    worksheet.write('H2', runDate)
    

    row = 1 # Starting Row (0 indexed)
    col = 0 # Starting Column (0 indexed) 
    

    n = len(Data) # Total number of rows
    print('Total number of rows: ',n)

    print('Writing Data into Worksheet')
        
    for Time, value1, value2, value3, value4, value5, value6 in (Data):
        # Writing Data in XLSX file
            
        worksheet.write(row, col, Time)
        worksheet.write(row, col+1, value1)
        worksheet.write(row, col+2, value2)
        worksheet.write(row, col+3, value3)
        worksheet.write(row, col+4, value4)
        worksheet.write(row, col+5, value5)
        worksheet.write(row, col+6, value6)
        row += 1

    chart1 = workbook.add_chart({'type': 'line'}) # adding chart of type 'Line' for Current values
    chart2 = workbook.add_chart({'type': 'line'}) # Chart for Voltage
    chart3 = workbook.add_chart({'type': 'line'}) # Chart for Power

        
    
    chart1.add_series({'name':['Sheet1',0,1],
                           'categories': ['Sheet1', 1,0,n,0],
                           'values': ['Sheet1', 1,1,n,1]
                           })
    chart2.add_series({'name':['Sheet1',0,2],
                           'categories': ['Sheet1', 1,0,n,0],
                           'values': ['Sheet1', 1,2,n,2]
                           })
    chart3.add_series({'name':['Sheet1',0,3],
                           'categories': ['Sheet1', 1,0,n,0],
                           'values': ['Sheet1', 1,3,n,3]
                           })
    
    chart1.set_title({'name': 'Current Chart'}) # Setting Title name
    chart1.set_x_axis({'name': 'Elapsed Time (s)'}) # Setting X-Axis name
    chart1.set_y_axis({'name': 'Value'}) # Setting Y-Axis name

    chart2.set_title({'name': 'Voltage Chart'})
    chart2.set_x_axis({'name': 'Elapsed Time (s)'})
    chart2.set_y_axis({'name': 'Value'})

    chart3.set_title({'name': 'Power Chart'})
    chart3.set_x_axis({'name': 'Elapsed Time (s)'})
    chart3.set_y_axis({'name': 'Value'})


    chart1.set_style(8) # Setting Chart Color
    chart2.set_style(5)
    chart2.set_style(9)

    worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10}) # Inserting Charts in the Worksheet
    worksheet.insert_chart('D2', chart2, {'x_offset': 25, 'y_offset': 10}) # //
    worksheet.insert_chart('D5', chart3, {'x_offset': 25, 'y_offset': 10}) # //




    workbook.close() # Closing Workbook 
    time.sleep(1)
    print('Sensor Writing successfull \n')





    
#-------------------------------------------------

def main():
    t1 = threading.Thread(target= looping)
    t2 = threading.Thread(target= IMU)
    t3 = threading.Thread(target= Sensor)
    
    

    t1.start() # start thread 1
    
    t2.start() # start thread 2
    t3.start() # start thread 3

    
    t1.join() # wait for the t1 thread to complete
    t2.join() # wait for the t2 thread to complete
    t3.join() # wait for the t3 thread to complete


#-----------------------------------------------------------


main() # Calling main

conn.close()
time.sleep(1)
print('Connection closed!')
