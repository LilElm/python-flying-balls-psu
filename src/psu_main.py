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
import multiprocessing.connection
multiprocessing.connection.BUFSIZE = 2**32-1 # This is the absolute limit for this PC
from multiprocessing import Process, Pipe
from gui import start_gui
#from gui import SignalStart
import sys
from itertools import cycle
import logging


class Channel():
   # def __init__(self, channel, name, i_final, done=False):
    def __init__(self, channel, name, done=False):
        self.channel = channel
        self.name = name
        #self.i_final = i_final
        self.done = done





def psu_currents(psu, channelDict, pipe_stopa, pipe_gui_innerb, pipe_gui_outerb):
    
    # Evaluate the current current and current profile
    for channel in channelDict:
        channelDict[channel].i_now = float(psu.query(f"ISET? {channelDict[channel].channel}"))
        print(f"{channelDict[channel].channel}: {channelDict[channel].i_now} Amps")
        
        
        channelDict[channel].done = False
        if channelDict[channel].tar == None:
            if channelDict[channel].dI == None:
                if channelDict[channel].dt == None:
                    channelDict[channel].done = True
        
        
        
        if not channelDict[channel].done:
            size = (channelDict[channel].tar - channelDict[channel].i_now) / channelDict[channel].dI
            if size < 0:
                size = size * -1
            size = int(math.ceil(size))
            channelDict[channel].profile_size = size
            channelDict[channel].profile = []
            val = channelDict[channel].i_now
            
            # Evaluate the direction of the profile
            if channelDict[channel].i_now < channelDict[channel].tar:
                for i in range(size-1):
                    val = val + channelDict[channel].dI
                    channelDict[channel].profile.append(val)
            else:
                for i in range(size-1):
                    val = val - channelDict[channel].dI
                    channelDict[channel].profile.append(val)
            channelDict[channel].profile.append(channelDict[channel].tar)
        

    
    
    time00 = time.time()
    for channel in channelDict:
        channelDict[channel].time0 = time00
        channelDict[channel].index = 0
    while True:
        if pipe_stopa.poll():
            while pipe_stopa.poll():
                pipe_stopa.recv()
            break
        
        
        for channel in channelDict:
            if not channelDict[channel].done:
                time1 = time.time()
                if time1 >= channelDict[channel].time0 + channelDict[channel].dt:
                    if channelDict[channel].index <= channelDict[channel].profile_size - 1:
                        psu.write(f"ISET {channelDict[channel].channel},{channelDict[channel].profile[channelDict[channel].index]}")
                        try:
                            channelDict[channel].i_now = float(psu.query(f"ISET? {channelDict[channel].channel}"))
                            t = time1 - time00
                            print(f"{t}: Channel {channel}: {channelDict[channel].i_now}")
                            channelDict[channel].pipeb.send([t, channelDict[channel].i_now])
                            channelDict[channel].time0 = channelDict[channel].time0 + channelDict[channel].dt
                            channelDict[channel].index = channelDict[channel].index + 1
                        except:
                            print("err")
                            print(str(psu.query(f"ISET? {channelDict[channel].channel}")))
                    else:
                        channelDict[channel].done = True
            
                    
        
        check = 0
        for channel in channelDict:
            if channelDict[channel].done:
                check = check + 1
        if check == len(channelDict):
            break
                    
        

    
    print("done")
    
    pipe_gui_innerb.send(False)
    pipe_gui_outerb.send(False)
    


def get_parameters(pipe_parama, channelDict):
    try:        
        # Wait for user input from GUI
        out_path = pipe_parama.recv()
        db_env = pipe_parama.recv()
        save = pipe_parama.recv()


        for channel in channelDict:
            channelDict[channel].tar = pipe_parama.recv()
            channelDict[channel].dI = pipe_parama.recv()
            channelDict[channel].dt = pipe_parama.recv()
            
            # Convert from mA to A
            if channelDict[channel].tar != None:
                channelDict[channel].tar = channelDict[channel].tar / 1000.0
            if channelDict[channel].dI != None:
                channelDict[channel].dI = channelDict[channel].dI / 1000.0
            
        

        """
        for channel in outer_channelDict:
            outer_channelDict[channel].tar = pipe_parama.recv() / 1000.0
            outer_channelDict[channel].dI = pipe_parama.recv() / 1000.0
            outer_channelDict[channel].dt = pipe_parama.recv()
        
        for channel in inner_channelDict:
            inner_channelDict[channel].tar = pipe_parama.recv()
            inner_channelDict[channel].dI = pipe_parama.recv()
            inner_channelDict[channel].dt = pipe_parama.recv()        
        """
        
    except Exception as e:
        print(str(e))
    return out_path, db_env, save, channelDict


# Main function
def main():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    address = 'GPIB0::10::INSTR'
    psu = rm.open_resource(address)
    
    
    
    # Create starting signal for GUI plots (deafult=False)
#    signal_start = SignalStart()
    
    # Create pipes for the GUI
    pipe_outputa, pipe_outputb = Pipe(duplex=False)
    pipe_parama, pipe_paramb = Pipe(duplex=False)
    
    pipe_stopa, pipe_stopb = Pipe(duplex=False)
    
    
    pipe_gui_innera, pipe_gui_innerb = Pipe(duplex=False)
    pipe_gui_outera, pipe_gui_outerb = Pipe(duplex=False)
    
    
    #pipe_signala, pipe_signalb = Pipe(duplex=False) # Restarts

    
   
    
        
        
    # Define all outer channels
    outer_channels = [(1, "CH1"),
                      (4, "CH4")]
    outer_channelDict = {channel: Channel(channel=channel, name=name) for channel, name in outer_channels}
   
        
    # Define all inner channels
    inner_channels = [(2, "CH2"),
                      (3, "CH3")]
    inner_channelDict = {channel: Channel(channel=channel, name=name) for channel, name in inner_channels}
   
        
        
    for channel in outer_channelDict:
        outer_channelDict[channel].pipea, outer_channelDict[channel].pipeb = Pipe(duplex=False)
    for channel in inner_channelDict:
        inner_channelDict[channel].pipea, inner_channelDict[channel].pipeb = Pipe(duplex=False)

    
    
     
    # Start GUI
    processlist = []
    proc0 = Process(target=start_gui, args=(outer_channelDict, inner_channelDict, pipe_paramb, pipe_stopb, pipe_gui_innera, pipe_gui_innerb, pipe_gui_outera, pipe_gui_outerb))
    processlist.append(proc0)
    proc0.start()
    
    
    
    
    
    # Start message function
    #msg0 = "Waiting for the camera"
    msg1 = "Waiting for user input"
    #msg2 = "Evaluating force profiles"
    #msg3 = "Starting acquisition"
    msg4 = "Acquiring data"
    msg5 = "Stop signal received"
    #proc1 = Process(target=message, args=(pipe_msga, msg0, ))
    #processlist.append(proc1)
    #proc1.start()
    
    
    
    channelDict = outer_channelDict | inner_channelDict
    while True:
        
        # Reset GUI
        #for channel in channelDict:
         #   channelDict[channel].pipe_reset.send(True)
        
        
        # Get input parameters from the GUI and evalute the force profile        
        out_path, db_env, save, channelDict = get_parameters(pipe_parama, channelDict)
        
        
        
        # Clear pipes
        if pipe_stopa.poll():
            while pipe_stopa.poll():
                pipe_stopa.recv()
        
        
        psu_currents(psu, channelDict, pipe_stopa, pipe_gui_innerb, pipe_gui_outerb)
        
        
        # Clear pipes
        if pipe_stopa.poll():
            while pipe_stopa.poll():
                pipe_stopa.recv()
        
        if pipe_parama.poll():
            while pipe_parama.poll():
                pipe_parama.recv()
        
    
    
    
    
    
    
    
    
    
    


# Function shows a pretty pinwheel
def message(pipe, msg="Loading"):
    time.sleep(1)
    while True:
        try:
            for frame in cycle(["|","/","-","\\"]):
                if pipe.poll():
                    msg = pipe.recv()
                    sys.stdout.write("\n")
                
                sys.stdout.write("\r" + msg + " " + frame)
                sys.stdout.flush()
                time.sleep(0.15)
            sys.stdout.write("\r")

        except KeyboardInterrupt:
            logging.warning("Pinwheel stopped via keyboard interruption")
    
    
    



# Run
if __name__ == "__main__":
    main()