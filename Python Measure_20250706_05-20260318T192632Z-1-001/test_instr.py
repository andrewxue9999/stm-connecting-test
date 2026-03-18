# -*- coding: utf-8 -*-
"""
Creates a test instrument wrapper for the python program (made for testing without instruments/gpib connections)

Ch0 always returns 0
Ch1 returns a random number between 0 and 1
"""
import numpy as np
import ast
import time

class TestInstr:
    ch_name=['z','rand']
    def __init__(self, name, address, channels):
        self.name=name
        self.gpib=address
        self.ch=ast.literal_eval(channels)
        self.output=0
        
        print('Connected to the tester ('+name+')!')
        
    def measure(self):
        msmt=[]
        if self.ch[0]:
            msmt.append(str(self.output))
        if self.ch[1]:
            msmt.append(str(np.sin(self.output*np.pi*2)))
        return msmt

    def header(self):
        hdr=[]
        for ind in range(len(self.ch)):
            if self.ch[ind]:
                hdr.append(self.name+'_'+self.ch_name[ind])
        return hdr
    
    def set_val(self, val):
        self.output=val
        
    def sweep_val(self, val, step, rate):
        num=int(np.abs((val-self.output)/step))
        wait=step/rate
        if (val-self.output)<0:
            step=-step
        for i in range(num):
            self.set_val(self.output+step)
            time.sleep(wait)
            
        self.set_val(val)
    