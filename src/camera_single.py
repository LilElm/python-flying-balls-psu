import asyncio
from bleak import BleakScanner, BleakClient


import numpy as np
import time
import logging
import datetime
import os

async def main():
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    os.makedirs(logfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "camera.log", encoding='utf-8', level=logging.INFO)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S")) 
    

    
    # Connect to the camera
    address = "CC:86:EC:72:D2:54"
    MODEL_NBR_UUID = "5DD3465F-1AEE-4299-8493-D2ECA2F8E1BB"
    async with BleakClient(address) as client:
        if client.is_connected:
            print("Connected to the camera")
        
        
        # Start recording
        input("Press RETURN to start program")
        data1 = bytearray([1,5,0,0,10,1,1,0,2,0,0,0])
        await client.write_gatt_char(MODEL_NBR_UUID, data1, response=True)
        print("Recording started")
        logging.info("Recording started")
        
        
    
                    
        # Stop recording
        input("Press RETURN to stop recording")
        data2 = bytearray([1,5,0,0,10,1,1,0,0,0,0,0])
        await client.write_gatt_char(MODEL_NBR_UUID, data2, response=True)
        print("Recording stopped")
        print("Closing Bluetooth connection")        
    input("Connection closed. Press RETURN to exit")
        

asyncio.run(main())
    




    
    
    #CC:86:EC:72:D2:54: A:91A496D3
    
    #https://pypi.org/project/bleak/
    #https://bleak.readthedocs.io/en/latest/
    #https://bleak.readthedocs.io/en/latest/usage.html