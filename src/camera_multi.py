"""# -*- coding: utf-8 -*-"""

# Import libraries
import asyncio
from bleak import BleakScanner, BleakClient
import logging
import datetime
import os
import sys


async def main():
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    os.makedirs(logfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "camera.log", encoding='utf-8', level=logging.INFO)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S")) 
    
    
    # Define the camera
    address = "CC:86:EC:72:D2:54"
    MODEL_NBR_UUID = "5DD3465F-1AEE-4299-8493-D2ECA2F8E1BB"
    
    # Connect to the camera
    logging.info("Attempting to connect to camera with:")
    logging.info(f"Address: {address}")
    logging.info(f"MODEL_NBR_UUID: {MODEL_NBR_UUID}")
    print("Attempting to connect to the camera")
    
    try:
        async with BleakClient(address) as client:
            if client.is_connected:
                print("Connected to the camera")
                logging.info("Connected to the camera")
                connected = True
            
            while connected:
                # Start recording
                input("Press RETURN to start recording")
                data1 = bytearray([1,5,0,0,10,1,1,0,2,0,0,0])
                logging.info("Sending 'START RECORDING' bytearray")
                print("Sending 'START RECORDING' bytearray")
                try:
                    await client.write_gatt_char(MODEL_NBR_UUID, data1, response=True)
                    print("Recording started")
                    logging.info("Recording started")
                except:
                    print("Failed to communicate with the camera")
                    logging.info("Failed to communicate with the camera")
                
                    
                # Stop recording 
                input("Press RETURN to stop recording")
                data2 = bytearray([1,5,0,0,10,1,1,0,0,0,0,0])
                logging.info("Sending 'START RECORDING' bytearray")
                print("Sending 'STOP RECORDING' bytearray")
                try:
                    await client.write_gatt_char(MODEL_NBR_UUID, data2, response=True)
                    print("Recording stopped")
                    logging.info("Recording stopped")
                except:
                    print("Failed to communicate with the camera")
                    logging.info("Failed to communicate with the camera")
     
                # Exit?
                answered = False
                while not answered:
                    ans = input("Enter 1 to restart or 0 to disconnect ")
                    if ans == '1':
                        connected = True
                        answered = True
                    elif ans == '0':
                        connected = False
                        answered = True
                        print("Please wait for the connection to close")
                    else:
                        answered = False
        print("Connection closed")
    except:
        logging.info("Failed to connect to the camera")
        print("Failed to connect to the camera")
        sys.exit(1)
                    
        
        

def start_camera():
    asyncio.run(main())
    




start_camera()
    
    #CC:86:EC:72:D2:54: A:91A496D3
    
    #https://pypi.org/project/bleak/
    #https://bleak.readthedocs.io/en/latest/
    #https://bleak.readthedocs.io/en/latest/usage.html