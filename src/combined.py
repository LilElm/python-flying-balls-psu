import asyncio
from bleak import BleakScanner, BleakClient

# Import libraries
import numpy as np
import time
import pyvisa
import datetime
import math
import logging
import os


class Channel():
    def __init__(self, channel, i_final, done=False):
        self.channel = channel
        self.i_final = i_final
        self.done = done



async def main():
    currentDT = datetime.datetime.now()
    logfolder = "../log/"
    os.makedirs(logfolder, exist_ok=True)
    logging.basicConfig(filename = logfolder + "main.log", encoding='utf-8', level=logging.INFO)
    logging.info(currentDT.strftime("%d/%m/%Y, %H:%M:%S"))  
    
    
    
    
    # Define the PSU
    rm = pyvisa.ResourceManager()
    #print(rm.list_resources())
    address = 'GPIB0::10::INSTR'
    psu = rm.open_resource(address)
    
    # Define the current/channel parameters
    dt = 1.0
    dI = 1.0
    channel_i = [(1, 1),
                 (2, 1),
                 (3, 1),
                 (4, 1)]
    channelDict = {channel: Channel(channel, i_final) for channel,i_final in channel_i}
    logging.info(f"dt = {dt}")
    logging.info(f"dI = {dI}")
    
    # Evaluate the current current and current profile
    for channel in channelDict:
        channelDict[channel].i_now = float(psu.query(f"ISET? {channelDict[channel].channel}"))
        print(f"{channelDict[channel].channel}: {channelDict[channel].i_now} Amps")
        logging.info(f"{channelDict[channel].channel}: {channelDict[channel].i_now} Amps")
        size = (channelDict[channel].i_final - channelDict[channel].i_now) / dI
        if size < 0:
            size = size * -1
        size = int(math.ceil(size))
        channelDict[channel].profile_size = size
        channelDict[channel].profile = []
        val = channelDict[channel].i_now
        
        # Evaluate the direction of the profile
        if channelDict[channel].i_now < channelDict[channel].i_final:
            for i in range(size-1):
                val = val + dI
                channelDict[channel].profile.append(val)
        else:
            for i in range(size-1):
                val = val - dI
                channelDict[channel].profile.append(val)
        channelDict[channel].profile.append(channelDict[channel].i_final)
    
    
        
    
    """
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)
    """
    
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
        time.sleep(1.0)        
        
        
        # Start PSU ramp
        time00 = time.time()
        time0 = time00
        index = 0
        while True:
            time1 = time.time()
            if time1 >= time0 + dt:
                for channel in channelDict:
                    if index <= channelDict[channel].profile_size - 1:
                        psu.write(f"ISET {channelDict[channel].channel},{channelDict[channel].profile[index]}")
                        channelDict[channel].i_now = float(psu.query(f"ISET? {channelDict[channel].channel}"))
                        t = time1 - time00
                        print(f"{t} seconds, Channel {channelDict[channel].channel}: {channelDict[channel].i_now} Amps")
                        logging.info(f"{t} seconds, Channel {channelDict[channel].channel}: {channelDict[channel].i_now} Amps")
                    else:
                        channelDict[channel].done = True
                index = index + 1 
                time0 = time0 + dt
                
                check = 0
                for channel in channelDict:
                    if channelDict[channel].done:
                        check = check + 1
                if check == len(channel_i):
                    break

                    
        # Stop recording
        print("Finished ramp")
        logging.info("Finished ramp")
        time.sleep(1.0)
        data2 = bytearray([1,5,0,0,10,1,1,0,0,0,0,0])
        await client.write_gatt_char(MODEL_NBR_UUID, data2, response=True)
        print("Recording stopped")
        print("Closing Bluetooth connection")        
    print("Connection closed. Press RETURN to exit.")
    input()
        

asyncio.run(main())
    




    
    
    #CC:86:EC:72:D2:54: A:91A496D3
    
    #https://pypi.org/project/bleak/
    #https://bleak.readthedocs.io/en/latest/
    #https://bleak.readthedocs.io/en/latest/usage.html