from PyQt5.QtWidgets import (QComboBox, 
        QGridLayout, QLabel, QLineEdit,
        QPushButton, QCheckBox,QFileDialog)
from PyQt5.QtGui import QDoubleValidator
from IntrumentsCommandsGUI_add import Commands
import numpy as np
import pyqtgraph as pg

class GUI_functions:
    
    def __init__(self, dic_instr):
        
        #Sets all the variables that you want to be accessible outside of class + Lists for ComboBox
        self.instr_types =  ['--None--','Keithley 2400','Keithley 2450', 'Keithley 6221', 'Yoko', 'SR830', 'SR860','Rotator','Janis Temperature','iTC 3He','Janis Magnet','SIM','tester', 'AMI Magnet', 'Bluefors Temperature', 'DSP 7265']
        self.dic_sweep =  ['Same direction', 'Raster']
        self.dic_instr = ['None']
        self.dic_instr.extend(dic_instr)
        self.fields = ['Internal Reference','ch1 display','ch2 display','Frequency','Amplitude','Time constant','Increase sensitivity','Decrease sensitivity']
        self.K_field = ['Disable','Output', 'Mode', 'Compliance', 'Range', 'Sweep To']
        self.K2450_field = ['Disable','Output', 'Mode', 'Reading mode', 'Compliance', 'Range', 'Sweep To']
        self.Y_field = ['Disable','Output', 'Mode', 'Range', 'Sweep To']
        self.Loop_field = ['Instr to sweep', 'Start', 'Stop', '# Points', 'Wait time (s)', 'Repeat', 'Sweep direction','# Points down']
        self.BLoop_field = ['Setpoint (T)', 'Ramp rate list (A/s)']
        self.TLoop_field = ['Setpoint (K)', 'Ramp rate (K/mn)', 'Heater Range']
        self.lockin_ch1Display = ['X', 'R']
        self.lockin_ch2Display = ['Y', 'Phase']
        self.lockin_tc_val = ['10e-6','30e-6','100e-6','300e-6','1e-3','3e-3','10e-3','30e-3','100e-3','300e-3','1','3','10','30','100','300','1e3','3e3','10e3','30e3']
        self.keithley_comp = ['--VOLTAGE MODE--','1.05e-6','10.5e-6', '105e-6','1.05e-3', '10.5e-3', '105e-3', '1.05','--CURRENT MODE--','210e-3','2.1','21','210']
        self.keithley_range = ['--VOLTAGE MODE--','200e-3','2','20','200','--CURRENT MODE--','1e-6','10e-6','100e-6','1e-3','10e-3','100e-3','1']
        self.keithley2450_range = ['--VOLTAGE MODE--','20e-3','200e-3','2','20','200','--CURRENT MODE--','10e-9','100e-9','1e-6','10e-6','100e-6','1e-3','10e-3','100e-3','1']
        self.yoko_range=['--VOLTAGE MODE--','10e-3','100e-3','1', '10','30','--CURRENT MODE','1e-3','10e-3','100e-3','200e-3']
        self.htr_range=['off', 'low', 'medium', 'high']
        self.instr1 = 0;self.instr2 = 0;self.instr3 = 0
        self.port1=0;self.port2=0;self.port3=0
        self.repeat1 = 0;self.repeat2 = 0;self.repeat3 = 0; self.B_repeat = 0;
        self.step1 = 0;self.step2 = 0;self.step3 = 0; self.B_range = 0;
        self.start1 = 0;self.start2 = 0;self.start3 = 0; self.B_start = 0;
        self.stop1 = 0;self.stop2 = 0;self.stop3 = 0; self.B_stop = 0;
        self.dir1 = 0;self.dir2 = 0;self.dir3 = 0
        self.wait1 = 0;self.wait2 = 0;self.wait3 = 0
        self.X1_plot = 0;self.X2_plot = 0;self.X3_plot = 0
        self.X1 = 0;self.X2 = 0;self.X3 = 0
        self.X1_immune = 0;self.X2_immune = 0;self.X3_immune = 0
        self.X1_rev = 0;self.X2_rev = 0;self.X3_rev = 0
        self.X1_list=[];self.X2_list=[];self.X3_list=[]
        self.pointdown1 = 0;self.pointdown2 = 0;self.pointdown3 = 0
        self.X1_SweepDown = 0;self.X2_SweepDown = 0;self.X3_SweepDown = 0;
        self.X1_meas_list=[]
        self.B_ramp = False; self.T_ramp = False;
        self.B_setpoint = 0; self.B_rampRate = 0; 
        self.T_setpoint = 0; self.T_rampRate = 0;
        self.BeginLoop = False
        self.dim_meas = 'None'
        self.func=np.zeros(2);
        self.save_filename = []
        self.L = ['name: ','folder: ','notes: ']
        self.browse_dir = False
        with open('Record_folder.txt','rt') as f:
            for i,line in enumerate(f):
                if i!=2:
                    self.save_filename.append(line.split(self.L[i])[1].replace('\n',''))
                else:
                    self.save_filename.append(line.split(self.L[i])[1].replace('\n','').replace('NEWLINE','\n'))
        
    def ValueInstr_GUI(self,instr): #Create a line with a checkbox, a colorbox to change color, a name and entry
        check_value = QCheckBox()
        color_value = pg.ColorButton()
        symbol_value = QComboBox()
        symbol_value.addItems(['-','o'])
        label_value = QLabel(instr)
        edit_value = QLineEdit()
        return check_value, color_value, symbol_value, label_value, edit_value
    
    def LoadInstr_GUI(self): #Create a line with a checkbox, a name and entry
        check_value = QCheckBox()
        instr_select = QComboBox()
        instr_select.addItems(self.instr_types)
        label_value = QLineEdit()
        edit_value = QLineEdit()
        # channel_selector = QPushButton('Select Data')
        return check_value, instr_select, label_value, edit_value#, channel_selector
    
    def save_GUI(self,frame): #Creates an entry to enter filename and browse to access folder
        self.CheckSave = QCheckBox('Save')
        self.CheckSave.setChecked(True)
        
        l1 = QLabel('Filename')
        self.filename_edit = QLineEdit()
        # self.filename_edit.setStyleSheet("color: #8e8e8e;\:disabled { background-color: #424242;}")
        self.filename_edit.insert(self.save_filename[0])
        self.CheckSave.toggled.connect(self.filename_edit.setEnabled)
        
        l2 = QLabel('Folder')
        self.folder_edit = QLineEdit()
        self.folder_edit.insert(self.save_filename[1])
        # self.folder_edit.setStyleSheet(':disabled { background-color: #424242;}')
        self.CheckSave.toggled.connect(self.folder_edit.setEnabled)
        l2_button = QPushButton('Browse')
        l2_button.clicked.connect(lambda: self.browse(self.folder_edit))
        self.CheckSave.toggled.connect(l2_button.setEnabled)
        
        if self.browse_dir == False:
            self.directory = self.save_filename[1]
        else:
            pass
        
        layout = QGridLayout()
        layout.addWidget(self.CheckSave,0,0,1,1)
        layout.addWidget(l1,1,0,1,1)
        layout.addWidget(self.filename_edit,1,1,1,1)
        layout.addWidget(l2,2,0,1,1)
        layout.addWidget(self.folder_edit,2,1,1,1)
        layout.addWidget(l2_button,2,2,1,1)
        layout.setRowStretch(3,2)
        frame.setLayout(layout)
        
    def browse(self,l): #Connect browse button to folders
        self.directory = QFileDialog.getExistingDirectory(directory=l.text())
        l.setText('{}'.format(self.directory))
        
    
    def lockin_GUI(self, lockin, label, lockin_Frame): #Create the apearence for lockins (830 and 860) moved
        j=0
        for i, f in enumerate(self.fields):
            if i in range(6):
                label[f] = QLabel(f)
            else:
                label[f] = None
            j+=1
        reference_entry = QCheckBox()
        ch1display_entry = QComboBox()
        ch1display_entry.addItems(self.lockin_ch1Display)
        ch2display_entry = QComboBox()
        ch2display_entry.addItems(self.lockin_ch2Display)
        freq_entry = QLineEdit(lockin_Frame)
        freq_entry.setDisabled(True)
        amp_entry = QLineEdit(lockin_Frame)
        amp_entry.setDisabled(True)
        reference_entry.toggled.connect(freq_entry.setEnabled)
        reference_entry.toggled.connect(amp_entry.setEnabled)
        tc_entry = QComboBox()
        tc_entry.addItems(self.lockin_tc_val)
        set_cmd = Commands(lockin)
        upsens_button = QPushButton('Increase sensitivity')
        upsens_button.clicked.connect(lambda: set_cmd.inc_sens_lockin())
        downsens_button = QPushButton('Decrease sensitivity')
        downsens_button.clicked.connect(lambda: set_cmd.dec_sens_lockin())
        set_button = QPushButton('Set lockin parameters')
        set_button.clicked.connect(lambda: set_cmd.set_lockin_param(reference_entry,ch1display_entry,ch2display_entry,freq_entry,amp_entry,tc_entry))
        layout = QGridLayout()
        for i, f in enumerate(self.fields):
            if i in range(6):
                layout.addWidget(label[f], i, 0, 1, 1)
        layout.addWidget(reference_entry, 0, 1, 1, 1)
        layout.addWidget(ch1display_entry, 1, 1, 1, 1)
        layout.addWidget(ch2display_entry, 2, 1, 1, 1)
        layout.addWidget(freq_entry, 3, 1, 1, 1)
        layout.addWidget(amp_entry, 4, 1, 1, 1)
        layout.addWidget(tc_entry, 5, 1, 1, 1)
        layout.addWidget(upsens_button, 6, 0, 1, 1)
        layout.addWidget(downsens_button, 6, 1, 1, 1)
        layout.addWidget(set_button, 7, 0, 1, 2)
        layout.setRowStretch(j+2, 2)
        lockin_Frame.setLayout(layout)
        
    def Keithely_GUI(self, instr, label, keithley_Frame, dico):#Apearence for Keithleys(2400 and 2450) moved
        j=0
        if instr.get_idn()['model'] == '2400': 
            for i, f in enumerate(self.K_field):
                label[f] = QLabel(f)
                j+=1
        else:
            for i, f in enumerate(self.K2450_field):
                label[f] = QLabel(f)
                j+=1
        protec_check = QCheckBox()    
        protec_check.setChecked(True)
        protec_button = None
        
        out_entry = None
        out_button = QPushButton('ON' if dico[0] == True else 'OFF')
        out_button.setEnabled(False)
        protec_check.toggled.connect(out_button.setDisabled)
        out_button.setStyleSheet("background-color: #008B45;" if dico[0] == True else "background-color: #CD4F39;")
        output_cmd = Commands(instr)
        out_button.clicked.connect(lambda: output_cmd.set_output(out_button))
            
        mode_entry = None
        mode_button = QPushButton('VOLT' if dico[1] in ['VOLT','voltage'] else 'CURR')
        mode_button.setEnabled(False)
        protec_check.toggled.connect(mode_button.setDisabled)
        mode_cmd = Commands(instr)
        mode_button.clicked.connect(lambda: mode_cmd.set_mode(mode_button,out_button))
        
        if instr.get_idn()['model'] == '2450':
            read_entry = None
            read_button = QPushButton('VOLT' if dico[2] in ['VOLT','voltage'] else 'CURR')
            read_button.setEnabled(False)
            protec_check.toggled.connect(read_button.setDisabled)
            read_cmd = Commands(instr)
            read_button.clicked.connect(lambda: read_cmd.set_read(read_button))

        comp_entry = QComboBox()
        comp_entry.addItems(self.keithley_comp)
        # if instr.get_idn()['model'] == '2400':
        #     comp_entry.addItems(self.keithley_comp)
        # else:
        #     comp_entry.addItems(self.keithley2450_comp)
        comp_button = QPushButton('Set')
        comp_cmd = Commands(instr)
        comp_button.clicked.connect(lambda: comp_cmd.set_compliance(comp_entry))
        
        range_entry = QComboBox()
        if instr.get_idn()['model'] == '2400':
            range_entry.addItems(self.keithley_range)
        else:
            range_entry.addItems(self.keithley2450_range)
        range_button = QPushButton('Set')
        range_cmd = Commands(instr)
        range_button.clicked.connect(lambda: range_cmd.set_range(range_entry))
        
        sweep_entry = QLineEdit(keithley_Frame)
        sweepTime_entry = QLineEdit(keithley_Frame)
        sweep_button = QPushButton('Set')
        sweep_cmd = Commands(instr)
        sweep_button.clicked.connect(lambda: sweep_cmd.sweep_to(sweepTime_entry,sweep_entry))
            
        layout = QGridLayout()
        if instr.get_idn()['model'] == '2400': 
            for i, f in enumerate(self.K_field):
                layout.addWidget(label[f], i, 0, 1, 1)
        else:
            for i, f in enumerate(self.K2450_field):
                layout.addWidget(label[f], i, 0, 1, 1)
        layout.addWidget(protec_check, 0, 1, 1, 2)
        layout.addWidget(protec_button, 0, 3, 1, 1)
        layout.addWidget(out_entry, 1, 1, 1, 2)
        layout.addWidget(out_button, 1, 3, 1, 1)
        layout.addWidget(mode_entry, 2, 1, 1, 2)
        layout.addWidget(mode_button, 2, 3, 1, 1)
        if instr.get_idn()['model'] == '2400': 
            layout.addWidget(comp_entry, 3, 1, 1, 2)
            layout.addWidget(comp_button, 3, 3, 1, 1)
            layout.addWidget(range_entry, 4, 1, 1, 2)
            layout.addWidget(range_button, 4, 3, 1, 1)
            layout.addWidget(QLabel('value'), 5, 1, 1, 1)
            layout.addWidget(QLabel('number of points'), 5, 2, 1, 1)
            layout.addWidget(sweep_entry, 6, 1, 1, 1)
            layout.addWidget(sweepTime_entry, 6, 2, 1, 1)
            layout.addWidget(sweep_button, 6, 3, 1, 1)
        else:
            layout.addWidget(read_entry, 3, 1, 1, 2)
            layout.addWidget(read_button, 3, 3, 1, 1)
            layout.addWidget(comp_entry, 4, 1, 1, 2)
            layout.addWidget(comp_button, 4, 3, 1, 1)
            layout.addWidget(range_entry, 5, 1, 1, 2)
            layout.addWidget(range_button, 5, 3, 1, 1)
            layout.addWidget(QLabel('value'), 6, 1, 1, 1)
            layout.addWidget(QLabel('number of points'), 6, 2, 1, 1)
            layout.addWidget(sweep_entry, 7, 1, 1, 1)
            layout.addWidget(sweepTime_entry, 7, 2, 1, 1)
            layout.addWidget(sweep_button, 7, 3, 1, 1)
        layout.setRowStretch(j+2, 3)
        keithley_Frame.setLayout(layout)
        
    def Yoko_GUI(self, instr, label, yoko_Frame, dico): #Apearence for Yokos
        j=0
        for i, f in enumerate(self.Y_field):
            label[f] = QLabel(f)
            j+=1
        protec_check = QCheckBox()    
        protec_check.setChecked(True)
        protec_button = None    
        
        out_entry = None
        out_button = QPushButton('ON' if dico[0] == 'on' else 'OFF')
        out_button.setEnabled(False)
        protec_check.toggled.connect(out_button.setDisabled)
        out_button.setStyleSheet("background-color: #008B45;" if dico[0] == 'on' else "background-color: #CD4F39;")
        output_cmd = Commands(instr)
        out_button.clicked.connect(lambda: output_cmd.set_output(out_button))

        mode_entry = None
        mode_button = QPushButton('VOLT' if dico[1]== 'VOLT' else 'CURR')
        mode_button.setEnabled(False)
        protec_check.toggled.connect(mode_button.setDisabled)
        mode_cmd = Commands(instr)
        mode_button.clicked.connect(lambda: mode_cmd.set_mode(mode_button,out_button))

        range_entry = QComboBox()
        range_entry.addItems(self.yoko_range)
        range_button = QPushButton('Set')
        range_cmd = Commands(instr)
        range_button.clicked.connect(lambda: range_cmd.set_range(range_entry))

        sweep_entry = QLineEdit(yoko_Frame)
        sweepTime_entry = QLineEdit(yoko_Frame)
        sweep_button = QPushButton('Set')
        sweep_cmd = Commands(instr)
        sweep_button.clicked.connect(lambda: sweep_cmd.sweep_to(sweepTime_entry,sweep_entry))
        layout = QGridLayout()
        for i, f in enumerate(self.Y_field):
            layout.addWidget(label[f], i, 0, 1, 1)
        layout.addWidget(protec_check, 0, 1, 1, 2)
        layout.addWidget(protec_button, 0, 3, 1, 1)
        layout.addWidget(out_entry, 1, 1, 1, 2)
        layout.addWidget(out_button, 1, 3, 1, 1)
        layout.addWidget(mode_entry, 2, 1, 1, 2)
        layout.addWidget(mode_button, 2, 3, 1, 1)
        layout.addWidget(range_entry, 3, 1, 1, 2)
        layout.addWidget(range_button, 3, 3, 1, 1)
        layout.addWidget(QLabel('value'), 4, 1, 1, 1)
        layout.addWidget(QLabel('number of points'), 4, 2, 1, 1)
        layout.addWidget(sweep_entry, 5, 1, 1, 1)
        layout.addWidget(sweepTime_entry, 5, 2, 1, 1)
        layout.addWidget(sweep_button, 5, 3, 1, 1)
        
        layout.setRowStretch(j+2, 3)
        yoko_Frame.setLayout(layout)
        
    def SIM_GUI(self, instr, sim_Frame): #Apearence for SIM
#        simcmd=Commands(instr)
        port={}
        vset={}
        batt={}
        sweep={}
        output={}
        #outbutton={}
        
        portdefault=[2,3,4]
        layout = QGridLayout()
        for i in range(len(portdefault)):
            port=QLineEdit(sim_Frame)
            port.setText(str(portdefault[i]))
            vset=QLineEdit(sim_Frame)
            vset.setText(simcmd.get_simvolt(portdefault[i]))
            step=QLineEdit(sim_Frame)
            step.setText('0.1')
            batt=QPushButton('Switch Battery')
            sweep=QPushButton('Sweep')
            output=QLineEdit('Output')
            output.setDisabled(True)
            simcmd.simoutput(output,portdefault[i])
            button=QPushButton('Toggle Output')
            button.clicked.connect(lambda state, outp=output, po=port: simcmd.togglesimoutput(outp,po))
            sweep.clicked.connect(lambda state, st=step,va=vset,po=port: simcmd.sim_voltsweep(st,va,po))
            
            layout.addWidget(QLabel('Port '+str(i)),0,3*i,1,1)
            layout.addWidget(QLabel('Setpoint (V) '),1,3*i,1,1)
            layout.addWidget(batt,3,3*i,1,1)
            layout.addWidget(sweep,3,3*i+1,1,1)
            layout.addWidget(vset,1,3*i+1,1,1)
            layout.addWidget(port,0,3*i+1,1,1)
            layout.addWidget(output,4,3*i,1,1)
            layout.addWidget(button,4,3*i+1,1,1)
            layout.addWidget(QLabel('Step Size (V)'),2,3*i,1,1)
            layout.addWidget(step,2,3*i+1,1,1)
        sim_Frame.setLayout(layout)

    def dsp_GUI(self, lockin, label, lockin_Frame): #Create the apearence for dsp7265 moved
        j=0
        for i, f in enumerate(self.fields):
            if i in range(6):
                label[f] = QLabel(f)
            else:
                label[f] = None
            j+=1
        reference_entry = QCheckBox()
        ch1display_entry = QComboBox()
        ch1display_entry.addItems(self.lockin_ch1Display)
        ch2display_entry = QComboBox()
        ch2display_entry.addItems(self.lockin_ch2Display)
        freq_entry = QLineEdit(lockin_Frame)
        freq_entry.setDisabled(True)
        amp_entry = QLineEdit(lockin_Frame)
        amp_entry.setDisabled(True)
        reference_entry.toggled.connect(freq_entry.setEnabled)
        reference_entry.toggled.connect(amp_entry.setEnabled)
        tc_entry = QComboBox()
        tc_entry.addItems(self.lockin_tc_val)
        set_cmd = Commands(lockin)
        upsens_button = QPushButton('Increase sensitivity')
        upsens_button.clicked.connect(lambda: set_cmd.inc_sens_lockin())
        downsens_button = QPushButton('Decrease sensitivity')
        downsens_button.clicked.connect(lambda: set_cmd.dec_sens_lockin())
        set_button = QPushButton('Set lockin parameters')
        set_button.clicked.connect(lambda: set_cmd.set_lockin_param(reference_entry,ch1display_entry,ch2display_entry,freq_entry,amp_entry,tc_entry))
        layout = QGridLayout()
        for i, f in enumerate(self.fields):
            if i in range(6):
                layout.addWidget(label[f], i, 0, 1, 1)
        layout.addWidget(reference_entry, 0, 1, 1, 1)
        layout.addWidget(ch1display_entry, 1, 1, 1, 1)
        layout.addWidget(ch2display_entry, 2, 1, 1, 1)
        layout.addWidget(freq_entry, 3, 1, 1, 1)
        layout.addWidget(amp_entry, 4, 1, 1, 1)
        layout.addWidget(tc_entry, 5, 1, 1, 1)
        layout.addWidget(upsens_button, 6, 0, 1, 1)
        layout.addWidget(downsens_button, 6, 1, 1, 1)
        layout.addWidget(set_button, 7, 0, 1, 2)
        layout.setRowStretch(j+2, 2)
        lockin_Frame.setLayout(layout)

    def RotatorLoopGUI(self, rotator, rotFrame): #rotator GUI
        rotcmd=Commands(rotator)
        
        initf0=rotator.getFrequency(0)
        initf1=rotator.getFrequency(1)
        initamp0=rotator.getAmplitude(0)
        initamp1=rotator.getAmplitude(1)
        inittheta=rotator.getPosition(0)
        initphi=rotator.getPosition(1)
        
        setTheta = QLineEdit(rotFrame)
        setTheta.setText("{:.2f}".format(inittheta))
        setPhi = QLineEdit(rotFrame)
        setPhi.setText("{:.2f}".format(initphi))
        
        frequencyTheta = QLineEdit(rotFrame)
        frequencyTheta.setText("{:.0f}".format(initf0))
        amplitudeTheta = QLineEdit(rotFrame)
        amplitudeTheta.setText("{:.0f}".format(initamp0))
        frequencyPhi = QLineEdit(rotFrame)
        frequencyPhi.setText("{:.0f}".format(initf1))
        amplitudePhi = QLineEdit(rotFrame)
        amplitudePhi.setText("{:.0f}".format(initamp1))
        
        amplitudeTheta.setValidator(QDoubleValidator(0,60,0))
        amplitudePhi.setValidator(QDoubleValidator(0,60,0))
        setTheta.setValidator(QDoubleValidator(0,60,2))
        setPhi.setValidator(QDoubleValidator(0,60,2))
        capacitancetheta = QLineEdit(rotFrame)
        capacitancetheta.setDisabled(True)
        capacitancephi = QLineEdit(rotFrame)
        capacitancephi.setDisabled(True)
        
        rotatetheta = QPushButton('Rotate Theta')
        rotatephi = QPushButton('Rotate Phi')
        groundtheta = QPushButton('Theta')
        groundtheta.clicked.connect(lambda: rotcmd.groundAxis(0,groundtheta))
        groundphi = QPushButton('Phi')
        groundphi.clicked.connect(lambda: rotcmd.groundAxis(1,groundphi))
        checkcapacitance=QPushButton('Check Capacitance')
        checkcapacitance.clicked.connect(lambda: rotcmd.checkCap(capacitancetheta,capacitancephi))
        rotcmd.checkCap(capacitancetheta,capacitancephi)
        rotcmd.checkGround(groundtheta,groundphi)
        
        rotatetheta.clicked.connect(lambda: rotcmd.setRotate(0,setTheta,frequencyTheta,amplitudeTheta,groundtheta))
        rotatephi.clicked.connect(lambda: rotcmd.setRotate(1,setPhi,frequencyPhi,amplitudePhi,groundphi))
        layout=QGridLayout()
        layout.addWidget(groundtheta,1,0,1,1)
        layout.addWidget(groundphi,2,0,1,1)
        layout.addWidget(QLabel('Capacitance (nF)'),0,1,1,1)
        layout.addWidget(QLabel('Frequency'),0,2,1,1)
        layout.addWidget(QLabel('Amplitude (0V-60V)'),0,3,1,1)
        layout.addWidget(QLabel('Set Point'),0,4,1,1)
        
        layout.addWidget(capacitancetheta,1,1,1,1)
        layout.addWidget(capacitancephi,2,1,1,1)
        layout.addWidget(frequencyTheta, 1,2,1,1)
        layout.addWidget(frequencyPhi, 2,2,1,1)
        layout.addWidget(amplitudeTheta, 1,3,1,1)
        layout.addWidget(amplitudePhi, 2,3,1,1)
        layout.addWidget(setTheta, 1,4,1,1)
        layout.addWidget(setPhi, 2,4,1,1)
        layout.addWidget(checkcapacitance, 3,0,2,1)
        layout.addWidget(rotatetheta, 1,5,1,1)
        layout.addWidget(rotatephi, 2,5,1,1)
        rotFrame.setLayout(layout)
    
    def BLoop_GUI(self, instr, label, B_Frame):
        j=0
        for i, f in enumerate(self.BLoop_field):
            label[f] = QLabel(f)
            j+=1
        self.stop_B = QLineEdit(B_Frame)
        self.ramp_B = QLineEdit(B_Frame)
        
        B_cmd = Commands(instr)
        self.start_Bramp = QPushButton('Ramp to setpoint')
        self.start_Bramp.clicked.connect(lambda: B_cmd.setB(self.stop_B,self.ramp_B))
        current_setpoint=B_cmd.getBTarget()
        current_rate=B_cmd.getBRate()
        self.stop_B.setText(str(current_setpoint))
        self.ramp_B.setText(str(current_rate))
        self.RTOZ_button = QPushButton('Ramp to 0 T')
        self.RTOZ_button.clicked.connect(lambda: B_cmd.Btozero())
        
        self.switch_status=QLineEdit()
        B_cmd.checkHtrStatus(self.switch_status)
        self.check_switch=QPushButton('Check Switch')
        self.check_switch.clicked.connect(lambda: B_cmd.checkHtrStatus(self.switch_status))
#        self.switch_on=QPushButton('Switch On')
#        self.switch_on.clicked.connect(lambda: B_cmd.htrOn())
#        self.switch_off=QPushButton('Switch Off')
#        self.switch_off.clicked.connect(lambda: B_cmd.htrOff())
        
        layout = QGridLayout()
        for i, f in enumerate(self.BLoop_field):
            layout.addWidget(label[f], i, 0, 1, 1)
        layout.addWidget(self.stop_B, 0, 1, 1, 1)
        layout.addWidget(self.ramp_B, 1, 1, 1, 1)
        layout.addWidget(self.start_Bramp, 2, 0, 1, 2)
        layout.addWidget(self.RTOZ_button, 3, 0, 1, 2)
        layout.addWidget(self.switch_status,4,0,1,1)
        layout.addWidget(self.check_switch,4,1,1,1)
#        layout.addWidget(self.switch_on,4,1,1,1)
#        layout.addWidget(self.switch_off,5,1,1,1)
        layout.setRowStretch(j+2, 2)
        B_Frame.setLayout(layout) 
        
    def TLoop_GUI(self, instr, label, T_Frame):
        j=0
        for i, f in enumerate(self.TLoop_field):
            label[f] = QLabel(f)
            j+=1
        self.stop_T = QLineEdit(T_Frame)
        self.ramp_T = QLineEdit(T_Frame)
        self.heatrange= QComboBox()
        self.heatrange.addItems(self.htr_range)
        currentsetpoint=instr.setpoint_2
        self.stop_T.setText(str(currentsetpoint))
        currentrate=instr.ramp_rate_2[1]
        self.ramp_T.setText(str(currentrate))
        T_cmd = Commands(instr)
        self.start_Tramp = QPushButton('Ramp')
        self.start_Tramp.clicked.connect(lambda: T_cmd.setT(self.stop_T,self.ramp_T, self.heatrange))
        htrrange=instr.heater_range_2
        idx=self.heatrange.findText(htrrange)
        if idx>=0:
            self.heatrange.setCurrentIndex(idx)

        layout = QGridLayout()
        for i, f in enumerate(self.TLoop_field):
            layout.addWidget(label[f], i, 0, 1, 1) 
        layout.addWidget(self.stop_T, 0, 1, 1, 1)
        layout.addWidget(self.ramp_T, 1, 1, 1, 1)
        layout.addWidget(self.heatrange, 2, 1, 1, 1)
        layout.addWidget(self.start_Tramp, 3, 0, 1, 2)
        layout.setRowStretch(j+1, 2)
        T_Frame.setLayout(layout) 
        
    def inLoop_GUI(self,label, loop_Frame):
        j=0
        for i, f in enumerate(self.Loop_field):
            label[f] = QLabel(f)
            j+=1
        self.instr_inloop = QComboBox()
        self.instr_inloop.addItems(self.dic_instr)
        self.start_inloop = QLineEdit(loop_Frame)
        self.start_inloop.setDisabled(True)
        self.stop_inloop = QLineEdit(loop_Frame)
        self.stop_inloop.setDisabled(True)
        self.step_inloop = QLineEdit(loop_Frame)
        self.step_inloop.setDisabled(True)
        self.wait_inloop = QLineEdit(loop_Frame)
        self.wait_inloop.setDisabled(True)
        self.repeat_inloop = QLineEdit(loop_Frame)
        self.repeat_inloop.setText('1')
        self.repeat_inloop.setDisabled(True)
#        self.port_inloop = QLineEdit(loop_Frame)
#        self.port_inloop.setText('1')
#        self.port_inloop.setDisabled(True)
        self.dir_inloop = QComboBox()
        self.dir_inloop.addItems(self.dic_sweep)
        self.sweepdown_inloop = QLineEdit(loop_Frame)
        self.sweepdown_inloop.setDisabled(True)
        self.dir_inloop.currentIndexChanged.connect(lambda: self.disable_Line2(self.dir_inloop,self.sweepdown_inloop))
        self.custum_inloop = QCheckBox("Custom sweep")
        self.function_inloop = QLineEdit(loop_Frame)
        self.function_inloop.setDisabled(True)
        self.custum_inloop.toggled.connect(self.function_inloop.setEnabled)
        self.custum_inloop.toggled.connect(self.start_inloop.setEnabled)
        self.custum_inloop.toggled.connect(self.stop_inloop.setEnabled)
        self.custum_inloop.toggled.connect(self.step_inloop.setEnabled)
        self.custum_inloop.toggled.connect(self.wait_inloop.setEnabled)
        self.custum_inloop.toggled.connect(self.repeat_inloop.setEnabled)
        self.list_inloop = QCheckBox("Custom List")
        self.listfunc_inloop = QLineEdit(loop_Frame)
        self.listfunc_inloop.setDisabled(True)
        self.list_inloop.toggled.connect(self.listfunc_inloop.setEnabled)
        self.list_inloop.toggled.connect(self.step_inloop.setEnabled)
        self.list_inloop.toggled.connect(self.wait_inloop.setEnabled)
        self.instr_inloop.currentIndexChanged.connect(lambda: self.disable_Line(self.instr_inloop,self.start_inloop,self.stop_inloop,self.step_inloop,self.wait_inloop,self.repeat_inloop,self.sweepdown_inloop))

        layout = QGridLayout()
        for i, f in enumerate(self.Loop_field):
            layout.addWidget(label[f], i, 0, 1, 1)
#        layout.addWidget(QLabel('Port'),0,2,1,1)
#        layout.addWidget(self.port_inloop,0,3,1,1)
        layout.addWidget(self.instr_inloop, 0, 1, 1, 1)
        layout.addWidget(self.start_inloop, 1, 1, 1, 3)
        layout.addWidget(self.stop_inloop, 2, 1, 1, 3)
        layout.addWidget(self.step_inloop, 3, 1, 1, 3)
        layout.addWidget(self.wait_inloop, 4, 1, 1, 3)
        layout.addWidget(self.repeat_inloop, 5, 1, 1, 3)
        layout.addWidget(self.dir_inloop, 6, 1, 1, 3)
        layout.addWidget(self.sweepdown_inloop, 7, 1, 1, 3)
        layout.addWidget(self.custum_inloop, 8, 0, 1, 1)
        layout.addWidget(self.function_inloop, 8, 1, 1, 1)
        layout.addWidget(self.list_inloop, 9, 0, 1, 1)
        layout.addWidget(self.listfunc_inloop, 9, 1, 1, 1)
        #layout.setRowStretch(j+3, 2)
        loop_Frame.setLayout(layout)
        
    def midLoop_GUI(self,label, loop_Frame):
        j=0
        for i, f in enumerate(self.Loop_field):
            label[f] = QLabel(f)
            j+=1
        self.instr_midloop = QComboBox()
        self.instr_midloop.addItems(self.dic_instr)
#        self.port_midloop = QLineEdit(loop_Frame)
#        self.port_midloop.setText('1')
#        self.port_midloop.setDisabled(True)
        self.start_midloop = QLineEdit(loop_Frame)
        self.start_midloop.setDisabled(True)
        self.stop_midloop = QLineEdit(loop_Frame)
        self.stop_midloop.setDisabled(True)
        self.step_midloop = QLineEdit(loop_Frame)
        self.step_midloop.setDisabled(True)
        self.wait_midloop = QLineEdit(loop_Frame)
        self.wait_midloop.setDisabled(True)
        self.repeat_midloop = QLineEdit(loop_Frame)
        self.repeat_midloop.setText('1')
        self.repeat_midloop.setDisabled(True)
        self.dir_midloop = QComboBox()
        self.dir_midloop.addItems(self.dic_sweep)
        self.sweepdown_midloop = QLineEdit(loop_Frame)
        self.sweepdown_midloop.setDisabled(True)
        self.dir_midloop.currentIndexChanged.connect(lambda: self.disable_Line2(self.dir_midloop,self.sweepdown_midloop))
        self.custum_midloop = QCheckBox("Custom sweep")
        self.function_midloop = QLineEdit(loop_Frame)
        self.function_midloop.setDisabled(True)
        self.custum_midloop.toggled.connect(self.function_midloop.setEnabled)
        self.custum_midloop.toggled.connect(self.start_midloop.setEnabled)
        self.custum_midloop.toggled.connect(self.stop_midloop.setEnabled)
        self.custum_midloop.toggled.connect(self.step_midloop.setEnabled)
        self.custum_midloop.toggled.connect(self.wait_midloop.setEnabled)
        self.custum_midloop.toggled.connect(self.repeat_midloop.setEnabled)
        self.list_midloop = QCheckBox("Custom List")
        self.listfunc_midloop = QLineEdit(loop_Frame)
        self.listfunc_midloop.setDisabled(True)
        self.list_midloop.toggled.connect(self.listfunc_midloop.setEnabled)
        self.list_midloop.toggled.connect(self.step_midloop.setEnabled)
        self.list_midloop.toggled.connect(self.wait_midloop.setEnabled)
        self.instr_midloop.currentIndexChanged.connect(lambda: self.disable_Line(self.instr_midloop,self.start_midloop,self.stop_midloop,self.step_midloop,self.wait_midloop,self.repeat_midloop,self.sweepdown_midloop))

        layout = QGridLayout()
        for i, f in enumerate(self.Loop_field):
            layout.addWidget(label[f], i, 0, 1, 1)
#        layout.addWidget(QLabel('Port'),0,2,1,1)
#        layout.addWidget(self.port_midloop,0,3,1,1)
        layout.addWidget(self.instr_midloop, 0, 1, 1, 1)
        layout.addWidget(self.start_midloop, 1, 1, 1, 3)
        layout.addWidget(self.stop_midloop, 2, 1, 1, 3)
        layout.addWidget(self.step_midloop, 3, 1, 1, 3)
        layout.addWidget(self.wait_midloop, 4, 1, 1, 3)
        layout.addWidget(self.repeat_midloop, 5, 1, 1, 3)
        layout.addWidget(self.dir_midloop, 6, 1, 1, 3)
        layout.addWidget(self.sweepdown_midloop, 7, 1, 1, 3)
        layout.addWidget(self.custum_midloop, 8, 0, 1, 1)
        layout.addWidget(self.function_midloop, 8, 1, 1, 1)
        layout.addWidget(self.list_midloop, 9, 0, 1, 1)
        layout.addWidget(self.listfunc_midloop, 9, 1, 1, 1)
        #layout.setRowStretch(j+3, 2)
        loop_Frame.setLayout(layout)
        
    def outLoop_GUI(self,label, loop_Frame):
        j=0
        for i, f in enumerate(self.Loop_field):
            label[f] = QLabel(f)
            j+=1
        self.instr_outloop = QComboBox()
        self.instr_outloop.addItems(self.dic_instr)
#        self.port_outloop = QLineEdit(loop_Frame)
#        self.port_outloop.setText('1')
#        self.port_outloop.setDisabled(True)
        self.start_outloop = QLineEdit(loop_Frame)
        self.start_outloop.setDisabled(True)
        self.stop_outloop = QLineEdit(loop_Frame)
        self.stop_outloop.setDisabled(True)
        self.step_outloop = QLineEdit(loop_Frame)
        self.step_outloop.setDisabled(True)
        self.wait_outloop = QLineEdit(loop_Frame)
        self.wait_outloop.setDisabled(True)
        self.repeat_outloop = QLineEdit(loop_Frame)
        self.repeat_outloop.setText('1')
        self.repeat_outloop.setDisabled(True)
        self.dir_outloop = QComboBox()
        self.sweepdown_outloop = QLineEdit(loop_Frame)
        self.sweepdown_outloop.setDisabled(True)
        self.dir_outloop.currentIndexChanged.connect(lambda: self.disable_Line2(self.dir_outloop,self.sweepdown_outloop))
        self.dir_outloop.addItems(self.dic_sweep)
        self.custum_outloop = QCheckBox("Custum sweep")
        self.function_outloop = QLineEdit(loop_Frame)
        self.function_outloop.setDisabled(True)
        self.custum_outloop.toggled.connect(self.function_outloop.setEnabled)
        self.custum_outloop.toggled.connect(self.start_outloop.setEnabled)
        self.custum_outloop.toggled.connect(self.stop_outloop.setEnabled)
        self.custum_outloop.toggled.connect(self.step_outloop.setEnabled)
        self.custum_outloop.toggled.connect(self.wait_outloop.setEnabled)
        self.custum_outloop.toggled.connect(self.repeat_outloop.setEnabled)
        self.list_outloop = QCheckBox("Custum List")
        self.listfunc_outloop = QLineEdit(loop_Frame)
        self.listfunc_outloop.setDisabled(True)
        self.list_outloop.toggled.connect(self.listfunc_outloop.setEnabled)
        self.list_outloop.toggled.connect(self.step_outloop.setEnabled)
        self.list_outloop.toggled.connect(self.wait_outloop.setEnabled)
        self.instr_outloop.currentIndexChanged.connect(lambda: self.disable_Line(self.instr_outloop,self.start_outloop,self.stop_outloop,self.step_outloop,self.wait_outloop,self.repeat_outloop,self.sweepdown_outloop,self.port_outloop))

        layout = QGridLayout()
        for i, f in enumerate(self.Loop_field):
            layout.addWidget(label[f], i, 0, 1, 1)
        layout.addWidget(self.instr_outloop, 0, 1, 1, 1)
#        layout.addWidget(QLabel('Port'),0,2,1,1)
#        layout.addWidget(self.port_inloop,0,3,1,1)
        layout.addWidget(self.start_outloop, 1, 1, 1, 3)
        layout.addWidget(self.stop_outloop, 2, 1, 1, 3)
        layout.addWidget(self.step_outloop, 3, 1, 1, 3)
        layout.addWidget(self.wait_outloop, 4, 1, 1, 3)
        layout.addWidget(self.repeat_outloop, 5, 1, 1, 3)
        layout.addWidget(self.dir_outloop, 6, 1, 1, 3)
        layout.addWidget(self.sweepdown_outloop, 7, 1, 1, 3)
        layout.addWidget(self.custum_outloop, 8, 0, 1, 1)
        layout.addWidget(self.function_outloop, 8, 1, 1, 1)
        layout.addWidget(self.list_outloop, 9, 0, 1, 1)
        layout.addWidget(self.listfunc_outloop, 9, 1, 1, 1)
        #layout.setRowStretch(j+3, 2)
        loop_Frame.setLayout(layout) 
        
    
    def disable_Line(self,box,widget1,widget2,widget3,widget4,widget5,widget6):#To disable line if no intrument to sweep
        if box.currentText()=='None':
            widget1.setDisabled(True)
            widget2.setDisabled(True)
            widget3.setDisabled(True)
            widget4.setDisabled(True)
            widget5.setDisabled(True)
            widget6.setDisabled(True)
            #widget7.setDisabled(True)
        elif box.currentText()=='sim':
            widget1.setEnabled(True)   
            widget2.setEnabled(True)   
            widget3.setEnabled(True)   
            widget4.setEnabled(True)   
            widget5.setEnabled(True) 
            widget6.setEnabled(True)
            #widget7.setEnabled(True)
        else:
            widget1.setEnabled(True)   
            widget2.setEnabled(True)   
            widget3.setEnabled(True)   
            widget4.setEnabled(True)   
            widget5.setEnabled(True) 
            widget6.setEnabled(True)
            #widget7.setDisabled(True)
            
    def disable_Line2(self,box,widget1):#To disable line if no raster sweep
        if box.currentText()=='Same direction':
            widget1.setEnabled(True)
        else:
            widget1.setDisabled(True)   
            
    def loop_param(self): #Reads all the parameters of the loops enties, create vector to sweep
        self.BeginLoop = True
        # if self.instr_inloop.currentText()!= 'None' and self.instr_midloop.currentText()=='None' and self.instr_outloop.currentText()=='None':
        if self.instr_inloop.currentText()!= 'None' and self.instr_midloop.currentText()=='None':
            self.dim_meas = '1D'
        # elif self.instr_inloop.currentText()!= 'None' and self.instr_midloop.currentText()!='None' and self.instr_outloop.currentText()=='None':
        elif self.instr_inloop.currentText()!= 'None' and self.instr_midloop.currentText()!='None':
            self.dim_meas = '2D'
        # elif self.instr_inloop.currentText()!= 'None' and self.instr_midloop.currentText()!='None' and self.instr_outloop.currentText()!='None':
            # self.dim_meas = '3D'
        else:
            self.dim_meas= 'Error'

        if self.dim_meas == '1D':
            self.instr1 = str(self.instr_inloop.currentText())
#            self.port1=int(self.port_inloop.text())
            self.instr2 = 'None'
            self.instr3 = 'None'
            self.repeat1 = int(self.repeat_inloop.text())
            self.repeat2 = None
            self.repeat3 = None
            self.step1 = int(self.step_inloop.text()) if len(self.step_inloop.text()) != 0 else None
            self.step3 = None
            self.start1 = float(self.start_inloop.text()) if len(self.start_inloop.text()) != 0 else None
            self.start2 = None
            self.start3 = None
            self.stop1 = float(self.stop_inloop.text()) if len(self.stop_inloop.text()) != 0 else None
            self.stop2 = None
            self.stop3 = None
            self.dir1 = self.dir_inloop.currentText()
            self.dir2 = None
            self.dir3 = None
            self.wait1 = float(self.wait_inloop.text())
            self.wait2 = None
            self.wait3 = None
            self.X1_immune = np.linspace(self.start1,self.stop1,self.step1) if len(self.step_inloop.text()) != 0 else None
            self.X2_immune = None
            self.X3_immune = None
            self.pointdown1 = int(self.sweepdown_inloop.text()) if len(self.sweepdown_inloop.text()) != 0 else None
            self.pointdown2 = None
            self.pointdown3 = None
            if self.custum_inloop.isChecked() == True:
                self.parse_custom(self.function_inloop.text())
                self.X1 = self.fonction(self.func,self.X1_immune) 
            elif self.list_inloop.isChecked() == True:
                for char in self.listfunc_inloop.text().split(','):
                    self.X1_list.append(float(char))
                self.X1 = self.X1_list
                self.step1 = len(self.X1)
            else:
                self.X1 = self.X1_immune
            self.X2 = None
            self.X3 = None
            self.X1_rev = self.X1[::-1]
            self.X2_rev = None
            self.X3_rev = None
            self.X1_SweepDown = np.linspace(self.X1[-1], self.X1[0], self.pointdown1) if len(self.sweepdown_inloop.text()) != 0 else None
            self.X2_SweepDown = None
            self.X3_SweepDown = None
            self.X1_plot = np.zeros((self.repeat1,self.step1))
            self.X2_plot = None
            self.X3_plot = None
            for i in range(self.repeat1):
                    for j in range(self.step1):
                        if self.dir1 == 'Same direction':
                            self.X1_plot[i][j] = self.X1[j]
                        else:
                            if i % 2 == 0:
                                self.X1_plot[i][j] = self.X1[j]
                            else:
                                self.X1_plot[i][j] = self.X1_rev[j]
        if self.dim_meas == '2D':
            self.instr1 = str(self.instr_inloop.currentText())
#            self.port1 = int(self.port_inloop.text())
            self.instr2 = str(self.instr_midloop.currentText())
#            self.port2 = int(self.port_midloop.text())
            self.instr3 = 'None'
            self.repeat1 = int(self.repeat_inloop.text())
            self.repeat2 = int(self.repeat_midloop.text())
            self.repeat3 = None
            self.step1 = int(self.step_inloop.text()) if len(self.step_inloop.text()) != 0 else None
            self.step2 = int(self.step_midloop.text()) if len(self.step_midloop.text()) != 0 else None
            self.step3 = None
            self.start1 = float(self.start_inloop.text()) if len(self.start_inloop.text()) != 0 else None
            self.start2 = float(self.start_midloop.text()) if len(self.start_midloop.text()) != 0 else None
            self.start3 = None
            self.stop1 = float(self.stop_inloop.text()) if len(self.stop_inloop.text()) != 0 else None
            self.stop2 = float(self.stop_midloop.text()) if len(self.stop_midloop.text()) != 0 else None
            self.stop3 = None
            self.dir1 = self.dir_inloop.currentText()
            self.dir2 = self.dir_midloop.currentText()
            self.dir3 = None
            self.wait1 = float(self.wait_inloop.text())
            self.wait2 = float(self.wait_midloop.text())
            self.wait3 = None
            self.X1_immune = np.linspace(self.start1,self.stop1,self.step1) if len(self.step_inloop.text()) != 0 else None
            self.X2_immune = np.linspace(self.start2,self.stop2,self.step2) if len(self.step_midloop.text()) != 0 else None
            self.X3_immune = None
            self.pointdown1 = int(self.sweepdown_inloop.text()) if len(self.sweepdown_inloop.text()) != 0 else None
            self.pointdown2 = int(self.sweepdown_midloop.text()) if len(self.sweepdown_midloop.text()) != 0 else None
            self.pointdown3 = None
            if self.custum_inloop.isChecked() == True:
                self.parse_custom(self.function_inloop.text())
                self.X1 = self.fonction(self.func,self.X1_immune) 
            elif self.list_inloop.isChecked() == True:
                for char in self.listfunc_inloop.text().split(','):
                    self.X1_list.append(float(char))
                self.X1 = self.X1_list
                self.step1 = len(self.X1)
            else:
                self.X1 = self.X1_immune
            if self.custum_midloop.isChecked() == True:
                self.parse_custom(self.function_midloop.text())
                self.X2 = self.fonction(self.func,self.X2_immune) 
            elif self.list_midloop.isChecked() == True:
                for char in self.listfunc_midloop.text().split(','):
                    self.X2_list.append(float(char))
                self.X2 = self.X2_list
                self.step2 = len(self.X2)
            else:
                self.X2 = self.X2_immune
            self.X3 = None
            self.X1_rev = self.X1[::-1]
            self.X2_rev = self.X2[::-1]
            self.X3_rev = None
            self.X1_SweepDown = np.linspace(self.X1[-1], self.X1[0], self.pointdown1) if len(self.sweepdown_inloop.text()) != 0 else None
            self.X2_SweepDown = np.linspace(self.X2[-1], self.X2[0], self.pointdown2) if len(self.sweepdown_midloop.text()) != 0 else None
            self.X3_SweepDown = None
            self.X1_plot = np.zeros((self.repeat1,self.step1))
            self.X2_plot = np.zeros((self.repeat2,self.step2))
            self.X3_plot = None
            for i in range(self.repeat2):
                for j in range(self.step2):
                    for k in range(self.repeat1):
                        for l in range(self.step1):
                            if self.dir2 == 'Same direction':
                                self.X2_plot[i][j] = self.X2[j]
                                if self.dir1 == 'Same direction':
                                    self.X1_plot[k][l] = self.X1[l]
                                else:
                                    if k % 2 == 0:
                                        self.X1_plot[k][l] = self.X1[l]
                                    else:
                                        self.X1_plot[k][l] = self.X1_rev[l]
                            else:
                                if i % 2 == 0:
                                    self.X2_plot[i][j] = self.X2[j]
                                else:
                                    self.X2_plot[i][j] = self.X2_rev[j]
                                if self.dir2 == 'Same direction':
                                    self.X1_plot[k][l] = self.X1[l]
                                else:
                                    if k % 2 == 0:
                                        self.X1_plot[k][l] = self.X1[l]
                                    else:
                                        self.X1_plot[k][l] = self.X1_rev[l]
        if self.dim_meas == '3D':
            self.instr1 = str(self.instr_inloop.currentText())
#            self.port1 = int(self.port_inloop.text())
            self.instr2 = str(self.instr_midloop.currentText())
#            self.port2 = int(self.port_midloop.text())
            self.instr3 = str(self.instr_outloop.currentText())
#            self.port3 = int(self.port_outloop.text())
            self.repeat1 = int(self.repeat_inloop.text())
            self.repeat2 = int(self.repeat_midloop.text())
            self.repeat3 = int(self.repeat_outloop.text())
            self.step1 = int(self.step_inloop.text())
            self.step2 = int(self.step_midloop.text())
            self.step3 = int(self.step_outloop.text())
            self.start1 = int(self.start_inloop.text())
            self.start2 = int(self.start_midloop.text())
            self.start3 = int(self.start_outloop.text())
            self.stop1 = int(self.stop_inloop.text())
            self.stop2 = int(self.stop_midloop.text())
            self.stop3 = int(self.stop_outloop.text())
            self.dir1 = self.dir_inloop.currentText()
            self.dir2 = self.dir_midloop.currentText()
            self.dir3 = self.dir_outloop.currentText()
            self.wait1 = float(self.wait_inloop.text())
            self.wait2 = float(self.wait_midloop.text())
            self.wait3 = float(self.wait_outloop.text())
            self.X1_plot = np.zeros((self.repeat1,self.step1))
            self.X2_plot = np.zeros((self.repeat2,self.step2))
            self.X3_plot = np.zeros((self.repeat3,self.step3))
            self.X1 = np.linspace(self.start1,self.stop1,self.step1)
            self.X2 = np.linspace(self.start2,self.stop2,self.step2)
            self.X3 = np.linspace(self.start3,self.stop3,self.step3)
            self.X1_rev = self.X1[::-1]
            self.X2_rev = self.X2[::-1]
            self.X3_rev = self.X3[::-1]
            self.pointdown1 = int(self.sweepdown_inloop.text())
            self.pointdown2 = int(self.sweepdown_midloop.text())
            self.pointdown3 = int(self.sweepdown_outloop.text())
            self.X1_SweepDown = np.linspace(self.stop1,self.start1,self.pointdown1)
            self.X2_SweepDown = np.linspace(self.stop2,self.start2,self.pointdown2)
            self.X3_SweepDown = np.linspace(self.stop3,self.start3,self.pointdown3)
            for i in range(self.repeat3):
                for j in range(self.step3):
                    for k in range(self.repeat2):
                        for l in range(self.step2):
                            for m in range(self.repeat1):
                                for n in range(self.step1):
                                    if self.dir3 == 'Same direction':
                                        self.X3_plot[i][j] = self.X3[j]
                                        if self.dir2 == 'Same direction':
                                            self.X2_plot[k][l] = self.X2[l]
                                            if self.dir1 == 'Same direction':
                                                self.X1_plot[m][n] = self.X1[n]
                                            else:
                                                if m % 2 == 0:
                                                    self.X1_plot[m][n] = self.X1[n]
                                                else:
                                                    self.X1_plot[m][n] = self.X1_rev[n]
                                        else:
                                            if k  %2 == 0:
                                                self.X2_plot[k][l] = self.X2[l]
                                            else:
                                                self.X2_plot[k][l] = self.X2_rev[l]
                                            if m % 2 == 0:
                                                self.X1_plot[m][n] = self.X1[n]
                                            else:
                                                self.X1_plot[m][n] = self.X1_rev[n]
                                    else:
                                        if i % 2 == 0:
                                            self.X3_plot[i][j] = self.X3[j]
                                        else:
                                            self.X3_plot[i][j] = self.X3_rev[j]
                                        if self.dir2 == 'Same direction':
                                            self.X2_plot[k][l] = self.X2[l]
                                            if self.dir1 == 'Same direction':
                                                self.X1_plot[m][n] = self.X1[n]
                                            else:
                                                if m % 2 == 0:
                                                    self.X1_plot[m][n] = self.X1[n]
                                                else:
                                                    self.X1_plot[m][n] =self. X1_rev[n]
                                        else:
                                            if k % 2 == 0:
                                                self.X2_plot[k][l] = self.X2[l]
                                            else:
                                                self.X2_plot[k][l] = self.X2_rev[l]
                                            if self.dir1 == 'Same direction':
                                                self.X1_plot[m][n] = self.X1[n]
                                            else:
                                                if m % 2 == 0:
                                                    self.X1_plot[m][n] = self.X1[n]
                                                else:
                                                    self.X1_plot[m][n] = self.X1_rev[n]
                                                    
                                                    
    def parse_custom(self,string):
        func_split=[]
        if '+' in string:
            string_split = string.split('+')
            if '-' in string_split[0]:
                string_split1 = string_split[0].split('-')
                for char in string_split1[1]:
                    func_split.append(char)
                self.func[0] = -float(func_split[0]) if func_split[0]!='X' else -1  
            else:
                for char in string_split[0]:
                    func_split.append(char)
                self.func[0] = float(func_split[0]) if func_split[0]!='X' else 1  
            self.func[1] = float(string_split[1]) 
        elif '-' in string:
            string_split = string.split('-')
            if len(string_split) == 3:
                for char in string_split[1]:
                    func_split.append(char)
                self.func[0] = -float(func_split[0]) if func_split[0]!='X' else -1  
                self.func[1] = -float(string_split[2])
            else:
                if string_split[0]!='':
                    for char in string_split[0]:
                        func_split.append(char)
                    self.func[0] = float(func_split[0]) if func_split[0]!='X' else 1
                    self.func[1] = -float(string_split[1])    
                else:
                    for char in string_split[1]:
                        func_split.append(char)
                    self.func[0] = -float(func_split[0]) if func_split[0]!='X' else -1
                    self.func[1] = 0
        else:
            for char in string:
                func_split.append(char)
            self.func[0] = float(func_split[0]) if func_split[0]!='X' else 1  
            self.func[1] = 0
            
    def fonction(self,f,X):
        return float(f[0])*X + float(f[1])
