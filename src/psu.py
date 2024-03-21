# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 17:19:01 2023

@author: ultservi
"""

## Control PSU via GPIB
## Change step function
# Output signals to channels 1&4 (Outer coils); 2&3 (Inner coils)


# -*- coding: utf-8 -*-

# Import libraries
import numpy as np
import pyvisa
import time
#from init import *
import datetime
import math



class Channel():
    def __init__(self, channel, i_final, done=False):
        self.channel = channel
        self.i_final = i_final
        self.done = done



# Main function
def main():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    address = 'GPIB0::10::INSTR'
    psu = rm.open_resource(address)
    
    dt = 1.0
    dI = 0.2
    #channels = [1,2,3,4]
    #i_finals = [1,0,0,0]
    #"""
    channel_i = [(1, 1.0),
                 (2, 1.5),
                 (3, 1.5),
                 (4, 1.2)]
    
    """
    channel_i = [(1, 0.0),
                 (2, 0.0),
                 (3, 0.0),
                 (4, 0.0)]
    #"""
    channelDict = {channel: Channel(channel, i_final) for channel,i_final in channel_i}
    
    
    
    
    

    
    
    # Evaluate the current current and current profile
    for channel in channelDict:
        channelDict[channel].i_now = float(psu.query(f"ISET? {channelDict[channel].channel}"))
        print(f"{channelDict[channel].channel}: {channelDict[channel].i_now} Amps")
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
        
    
    input("===============")

    
    
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
                    print(f"{t}: {channelDict[channel].i_now}")
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
                    
            
            print("=================")

    
    input("done")
    
    
    
    
    
    
    
    



# Run
if __name__ == "__main__":
    main()