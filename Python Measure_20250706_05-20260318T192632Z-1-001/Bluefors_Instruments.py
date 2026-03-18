import json
import requests
import ast
import pyvisa
import datetime
from PyQt5.QtWidgets import (QComboBox, 
        QGridLayout, QLabel, QLineEdit,
        QPushButton, QCheckBox,QFileDialog, QMessageBox, QTabWidget, QWidget)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtTest import QTest
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()

class Bluefors_Temp:
    T_field=['Heater Output (mW)']
    ch_name=['mxc','mxc_heater']
    #htr_range=['off', 'low', 'medium', 'high']
    ctrl_label=['Heater Output (mW)']
    #measure_every=100
    measure_every=1
    def __init__(self, name):
        self.name=name
        self.ch=[True,True]
        self.DEVICE_IP = '128.59.39.193'
        self.TIMEOUT = 5
        self.htr=0
        self.url = 'http://{}:5001/channel/measurement/latest'.format(self.DEVICE_IP) 
        
        check=False
        stop=datetime.datetime.now(datetime.timezone.utc)
        start=stop-datetime.timedelta(hours=1)
        # print(stop.isoformat(timespec='seconds').split('+')[0]+'Z')
        start=start.isoformat(timespec='seconds').split('+')[0]+'Z'
        stop=stop.isoformat(timespec='seconds').split('+')[0]+'Z'
        initdata={'channel_nr': 6, 'start_time':start,'stop_time':stop,'fields':['temperature']}
        req = requests.post('http://128.59.39.193:5001/channel/historical-data',json=initdata, timeout=self.TIMEOUT)
        data = req.json()
        self.T_MXC=data['measurements']['temperature'][-1]
        
        self.msmtcount=0
        print('Connected to MXC thermometer ('+name+')!')
    
    def measure(self):
        if self.msmtcount==self.measure_every:
    
            req = requests.get(self.url, timeout=self.TIMEOUT)
            data = req.json()
            temp_json = json.dumps(data, indent=2)
            temp_dict = json.loads(temp_json)
            if temp_dict['channel_nr'] == 6:
                self.T_MXC = temp_dict['temperature']
            else:
                self.T_MXC = self.T_MXC
            self.msmtcount=0
        else:
            self.msmtcount+=1
        msmt=[str(self.T_MXC), str(self.htr)]
        return msmt

    def header(self):
        hdr=[]
        for ind in range(len(self.ch)):
            if self.ch[ind]:
                hdr.append(self.name+'_'+self.ch_name[ind])
        return hdr
    
    def control_GUI(self, frame):
        label={}
        j=0
        for i, f in enumerate(self.ctrl_label):
            label[f] = QLabel(f)
            j+=1
        self.stop_T = QLineEdit(frame)
        self.start_Tramp = QPushButton('Ramp')
        self.start_Tramp.clicked.connect(lambda: self.set_temp(self.stop_T))

        layout = QGridLayout()
        for i, f in enumerate(self.ctrl_label):
            layout.addWidget(label[f], i, 0, 1, 1) 
        layout.addWidget(self.stop_T, 0, 1, 1, 1)
        layout.addWidget(self.start_Tramp, 2, 0, 1, 2)
        layout.setRowStretch(j+1, 2)
        frame.setLayout(layout) 
        

    def set_val(self, value): #takes value in mW
        value=value/1000
        self.htr=value
        seturl = 'http://{}:5001/heater/update'.format(self.DEVICE_IP) 
        data={'heater_nr': 4, 'active':True,'pid_mode':0,'power':value}
        req = requests.post(seturl,json=data, timeout=self.TIMEOUT)
        
    def sweep_val(self,val, pts, wait): #Sets value instead of sweeping
        self.set_val(val)
        self.htr=val
        
    def set_temp(self, Tsetp):
        setpoint = float(Tsetp.text())
        self.set_val(setpoint)


class AMI430:
    ctrl_label=['Field Setpoint']
    def __init__(self, name):
        self.name=name
        # self.ch=ast.literal_eval(channels)
        self.instr=rm.open_resource("TCPIP0::128.59.247.54::7180::SOCKET")
        self.instr.read_termination='\r\n'
        self.instr.write_termination='\r\n'
        print('Connected to: ' + str(self.instr.query('*IDN?')))
        self.instr.read()
        self.instr.read()
    
    def measure(self):
        b=self.instr.query("FIELD:MAGnet?")
        msmt=[b]
        return msmt

    def header(self):
        hdr=['B']
        return hdr
    
    def control_GUI(self, frame):
        tab_B = QTabWidget()
        tab_set = QWidget()
        tab_ramp = QWidget()
        tab_B.addTab(tab_set,'Setpoint')
        tab_B.addTab(tab_ramp,'Ramp Rate')
        
        label={}
        j=0
        for i, f in enumerate(self.ctrl_label):
            label[f] = QLabel(f)
            j+=1
        self.field_set = QLineEdit(frame)
        currentsetpoint=self.current_setpoint()
        self.field_set.setText(str(currentsetpoint))
        self.start_ramp = QPushButton('Ramp')
        self.pause = QPushButton('Pause')
        self.start_ramp.clicked.connect(lambda: self.set_B(self.field_set))
        self.pause.clicked.connect(self.pause_ramp)

        layout = QGridLayout()
        for i, f in enumerate(self.ctrl_label):
            layout.addWidget(label[f], i, 0, 1, 1) 
        layout.addWidget(self.field_set, 0, 1, 1, 1)
        layout.addWidget(self.pause, 1, 1, 1, 1)
        layout.addWidget(self.start_ramp, 2, 0, 1, 2)
        
        tab_set.setLayout(layout)
        
        seg=int(self.instr.query('RAMP:RATE:SEG?'))
        rlabel={}
        self.rset={}
        ratelayout=QGridLayout()
        for i in range(seg):
            s=i+1
            top=self.instr.query('RAMP:RATE:FIELD:'+str(s)+'?').split(',')[1]
            rlabel[i]=QLabel('Segment '+str(s)+'(to '+top+' T)')
            self.rset[i]=QLineEdit()
            self.rset[i].setText(self.instr.query('RAMP:RATE:FIELD:'+str(s)+'?').split(',')[0])
            ratelayout.addWidget(rlabel[i],i,0,1,1)
            ratelayout.addWidget(self.rset[i],i,1,1,1)
        setrate=QPushButton('Set Rates')
        ratelayout.addWidget(setrate,seg,1,1,1)
        setrate.clicked.connect(lambda: self.set_rate(self.rset))
        
        tab_ramp.setLayout(ratelayout)
        
        lo=QGridLayout()
        lo.addWidget(tab_B,0,0,0,0)
        
        frame.setLayout(lo) 
        
    def current_setpoint(self):
        return self.instr.query('FIELD:TARG?')
    
    def set_B(self, value):
        setpoint=str(value.text())
        num=float(setpoint)
        if num>12:
            setpoint='12'
        elif num<-12:
            setpoint='-12'
        
        self.instr.write('CONF:FIELD:TARG '+setpoint)
        self.instr.write('RAMP')
        
    def pause_ramp(self):
        self.instr.write('PAUSE')

    def set_rate(self, seglist):
        i=1
        print(seglist[0])
        for j in seglist:
            rate=seglist[j].text()
            to=self.instr.query('RAMP:RATE:FIELD:'+str(i)+'?').split(',')[1]
            self.instr.write('CONF:RAMP:RATE:FIELD '+str(i)+','+str(rate)+','+to)
            i+=1
        