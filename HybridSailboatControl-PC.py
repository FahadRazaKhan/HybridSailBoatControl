# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 13:06:23 2018

@author: fahad
"""

import socket
import sys
import time
import threading


#-------------Initialization-----------------------------------
def tcp1():
    TCP_IP = '192.168.31.148'
    TCP_PORT = 50007
    BUFFER_SIZE = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Client socket1 is created \n')
    try:
        s.connect((TCP_IP, TCP_PORT))
        print(' TCP1 Connected \n')
    except:
        print('An Error Occured! \n')
        sys.exit()
   
    
    MESSAGE = input('Please press A and Enter to continue ')
    message_bytes = MESSAGE.encode('utf-8') ## Converting into Bytes
    s.sendall(message_bytes)
    time.sleep(0.2) ## 0.2 second delay
    
    
    
    #-------------------Sending Commands ----------------------------
    
    global flag
    flag = False
    print('Please Enter W for forward motion, A for moving Left, D for moving Right, S to stop, and C to Exit')
    while True:
        
        MESSAGE = input('Please Enter Command ')
        message_bytes = MESSAGE.encode('utf-8') ## Converting into Bytes
        s.sendall(message_bytes)
        if MESSAGE.upper() == 'C':
            flag = True
            break
                
        time.sleep(0.2) ## 0.2 second pause
    
    data = s.recv(BUFFER_SIZE)
    print (data.decode('utf-8'))
    s.close()
    time.sleep(0.5) ## 0.5 second delay
    print('TCP1 Communication Closed') 
#----------------------------------------------------------------




def main():
    t1= threading.Thread(target= tcp1)
    
    
    t1.start()
    
    
    t1.join()
    
    
flag = False # Initialization   
main()    

