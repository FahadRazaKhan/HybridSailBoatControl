# HybridSailBoatControl
Manual Control of hybrid sailboat

This code controls main sail, rudders, and two electric motors mounted on a toy sailboat. A TCP connection is established first 
between RaspberryPi controller and a PC. User can send commands to control sail, rudders and electric motors on the boat. This program also
reads and records two sensors in real-time. First, a current sensor which measures current, voltage , and power consumption of the boat
and second an IMU which gives the heading (Yaw), roll, and pitch angles of the boat.
