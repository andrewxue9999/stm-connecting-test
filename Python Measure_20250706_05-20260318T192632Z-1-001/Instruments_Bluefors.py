# from qcodes.instrument_drivers.stanford_research.SR830 import SR830
# from qcodes.instrument_drivers.stanford_research.SR86x import SR86x
# from qcodes.instrument_drivers.yokogawa.GS200 import GS200
# from qcodes.instrument_drivers.tektronix.Keithley_2400 import Keithley_2400
# from qcodes.instrument_drivers.tektronix.Keithley_2450 import Keithley2450
# from lakeshore331_test import LakeShore331
# from lakeshore_625_magnet_driver import Model_625
# from PyANC350v4 import Positioner
from test_instr import TestInstr
from Measurement_Instruments import SR830_inst, SR860_inst, K2400_inst, SIM_inst, yoko_inst, K6221_inst, DSP7265_inst
#from Oxford_3He_instr import MercuryiTC
#from Janis_Instruments import LakeShore335, LakeShore625
from Bluefors_Instruments import Bluefors_Temp, AMI430
import time
# import visa

# rm = visa.ResourceManager()

class Instruments:
    
    def __init__(self):
        
        self.dic={}
        self.list_names=[];self.list_instr=[];self.list_gpib=[];self.list_ch=[]
        self.instr=[]
        self.lockins=[]
        self.not_lockins=[]
        self.read_file()
        
        
        for ind in range(len(self.list_names)):
            gpib='GPIB0::'+self.list_gpib[ind]+'::INSTR'
            if self.list_instr[ind]=='SR830':
                li=SR830_inst(self.list_names[ind],gpib,self.list_ch[ind])
                self.instr.append(li)
                self.lockins.append(li)
            elif self.list_instr[ind]=='SR860':
                li860=SR860_inst(self.list_names[ind],gpib,self.list_ch[ind])
                self.instr.append(li860)   
            elif self.list_instr[ind]=='Keithley 2400':
                k=K2400_inst(self.list_names[ind],gpib,self.list_ch[ind])
                self.instr.append(k)
                self.not_lockins.append(k)
            elif self.list_instr[ind]=='Keithley 6221':
                k6=K6221_inst(self.list_names[ind],gpib)
                self.instr.append(k6)
                self.not_lockins.append(k6)
            elif self.list_instr[ind]=='Yoko':
                y=yoko_inst(self.list_names[ind],gpib,self.list_ch[ind])
                self.instr.append(y)
                self.not_lockins.append(y)
            elif self.list_instr[ind]=='Bluefors Temperature':
                temp=Bluefors_Temp(self.list_names[ind])
                self.instr.append(temp)
                self.not_lockins.append(temp)
            elif self.list_instr[ind]=='AMI Magnet':
                magnet=AMI430(self.list_names[ind])
                self.instr.append(magnet)
                self.not_lockins.append(magnet)
            elif self.list_instr[ind]=='SIM':
                sim=SIM_inst(self.list_names[ind],gpib,self.list_ch[ind])
                self.instr.append(sim)
                self.not_lockins.append(sim)
            elif self.list_instr[ind]=='DSP 7265':
                dsp=DSP7265_inst(self.list_names[ind],gpib,self.list_ch[ind])
                self.instr.append(dsp)
                self.lockins.append(dsp)
            elif self.list_instr[ind]=='tester':
                self.instr.append(TestInstr(self.list_names[ind],self.list_gpib[ind],self.list_ch[ind]))
                
            else:
                pass
        self.hdr=self.header()
        
    def header(self):
        hdr=[]
        for inst in self.instr:
            hdr.extend(inst.header())
        return hdr
    
    def measure(self):
        # st=time.time()
        msmt=[]
        for inst in self.instr:
            msmt.extend(inst.measure())
            # print(time.time()-st)
            
        return msmt
    def read_file(self):
        with open('Instruments.txt', 'rt') as f:
            for line in f:
                if line.startswith('Name')==True:
                    self.list_names.append(line.split('=')[1].rstrip())
                elif line.startswith('Instrument')==True:
                    self.list_instr.append(line.split('=')[1].rstrip())
                elif line.startswith('GPIB')==True:
                    self.list_gpib.append(line.split('=')[1].rstrip())
                elif line.startswith('channels')==True:
                    self.list_ch.append(line.split('=')[1].rstrip())
                else:
                    pass
                
    def get_instr(self, name):
        return self.instr[self.list_names.index(name)]
        