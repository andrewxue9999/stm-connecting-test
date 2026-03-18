import numpy as np
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QMessageBox
keithley2450_comp = ['--READ CURRENT MODE--','10e-9','100e-9','1e-6','10e-6', '100e-6','1e-3', '10e-3', '100e-3', '1','--READ VOLTAGE MODE--','210e-3','2.1','21','210']
class Commands:
    def __init__(self,instr):
        self.instr = instr
        
    def set_lockin_param(self,ref,display1,display2,freq,amp,tc):
        if self.instr.amplitude() < 0.004:
            amp_start = 0.004
        elif self.instr.amplitude() > 5:
            amp_start = 5
        else:
            amp_start = self.instr.amplitude()
        if ref.isChecked()==True:
            if self.instr.get_idn()['model'] == 'SR830':
                self.instr.reference_source('internal')
            else:
                pass
        else:
            if self.instr.get_idn()['model'] == 'SR830':
                self.instr.reference_source('external')
            else:
                pass
        if self.instr.get_idn()['model'] == 'SR830':
            self.instr.ch1_display(display1.currentText())
            self.instr.ch2_display(display2.currentText())
        if len(freq.text()) == 0:
            pass
        else:
            self.instr.frequency(float(freq.text()))
        if len(amp.text()) == 0:
            pass
        else:
            if float(amp.text())>5:
                amplitude = 5
            elif float(amp.text())<0.004:
                amplitude = 0.004
            else:
                amplitude = float(amp.text())
            L = np.linspace(amp_start,amplitude, 21)
            for amp in L:
                self.instr.amplitude(amp)
                QTest.qWait(int(0.1*1000))
        print('Setting time constant:' + tc.currentText())
        self.instr.time_constant(float(tc.currentText()))
                
    def inc_sens_lockin(self):
        print('Sensitivity set to' + str(self.instr.sensitivity()))
        self.instr.increment_sensitivity()
        
    def dec_sens_lockin(self):
        print('Sensitivity set to' + str(self.instr.sensitivity()))
        self.instr.decrement_sensitivity()
        
    def set_output(self,val):
        if 'yoko' in str(self.instr):
            if self.instr.output()=='on':
                self.instr.off()
                val.setText('OFF')
                val.setStyleSheet("background-color: #CD4F39;")
            else:
                self.instr.on()
                val.setText('ON')
                val.setStyleSheet("background-color: #008B45;")
        elif 'keithley' in str(self.instr):
            if self.instr.get_idn()['model'] == '2400':
                if self.instr.output()==True:
                    self.instr.output(False)
                    val.setText('OFF')
                    val.setStyleSheet("background-color: #CD4F39;")
                else:
                    self.instr.output(True)
                    val.setText('ON')
                    val.setStyleSheet("background-color: #008B45;")
            elif self.instr.get_idn()['model'] == '2450':
                if self.instr.output_enabled() == True:
                    self.instr.output_enabled(False)
                    val.setText('OFF')
                    val.setStyleSheet("background-color: #CD4F39;")
                else:
                    self.instr.output_enabled(True)
                    val.setText('ON')
                    val.setStyleSheet("background-color: #008B45;")
            else:
                pass
        else:
            pass

    def set_mode(self,val,out):
        if 'yoko' in str(self.instr):
            if self.instr.source_mode()=='CURR':
                self.instr.source_mode('VOLT')
                val.setText('VOLT')
            else:
                self.instr.source_mode('CURR')
                val.setText('CURR')
                
        elif 'keithley' in str(self.instr):
            if self.instr.get_idn()['model'] == '2400':
                if self.instr.mode()=='CURR':
                    val.setText('VOLT')
                    self.instr.mode('VOLT')
                    out.setText('OFF')
                    out.setStyleSheet("background-color: #CD4F39;")
                    
                else:
                    val.setText('CURR')
                    self.instr.mode('CURR')
                    out.setText('OFF')
                    out.setStyleSheet("background-color: #CD4F39;")
            elif self.instr.get_idn()['model'] == '2450':
                if self.instr.source.function() == 'current':
                    val.setText('VOLT')
                    self.instr.source.function('voltage')
                    out.setText('OFF')
                    out.setStyleSheet("background-color: #CD4F39;")
                else:
                    val.setText('CURR')
                    self.instr.source.function('current')
                    out.setText('OFF')
                    out.setStyleSheet("background-color: #CD4F39;")
        else:
            pass
        
    def set_read(self,val):
        if self.instr.sense.function() == 'current':
            self.instr.sense.function('voltage')
            val.setText('VOLT')
        elif self.instr.sense.function() == 'voltage':
            self.instr.sense.function('current')
            val.setText('CURR')

    def set_compliance(self,val):
        value = float(val.currentText())
        index = val.currentIndex()
        value2 =float( keithley2450_comp[index])
        if 'keithley' in str(self.instr):
            if self.instr.get_idn()['model'] == '2400':
                if self.instr.mode() == 'CURR':
                    self.instr.compliancev(value)
                else:
                    self.instr.compliancei(value)
            else:
                self.instr.sense.range(value2)
                self.instr.source.limit(value)
            
    def set_range(self,val):
        value = float(val.currentText())
        if 'yoko' in str(self.instr):
            if self.instr.source_mode()=='CURR':
                self.instr.current_range(value)
            else:
                self.instr.voltage_range(value)
        if 'keithley' in str(self.instr):
            if self.instr.get_idn()['model'] == '2400':
                if self.instr.mode() == 'CURR':
                    self.instr.rangei(value)
                else:
                    self.instr.rangev(value)
            else:
                self.instr.source.range(value)
        
    def sweep_to(self,ste,val):
        value = float(val.text())
        step = float(ste.text())
        if 'yoko' in str(self.instr):
            if self.instr.source_mode()=='CURR':
                for i in np.linspace(self.instr.current(),value,step):
                    self.instr.current(i)
                    QTest.qWait(int(0.1*1000))
            else:
                for i in np.linspace(self.instr.voltage(),value,step):
                    self.instr.voltage(i)
                    QTest.qWait(int(0.1*1000))
        if 'keithley' in str(self.instr):
            if self.instr.get_idn()['model'] == '2400':
                if self.instr.mode()=='CURR':
                    for i in np.linspace(self.instr.curr(),value,step):
                        self.instr.curr(i)
                        QTest.qWait(int(0.1*1000))
                else:
                    for i in np.linspace(self.instr.volt(),value,step):
                        self.instr.volt(i)
                        QTest.qWait(int(0.1*1000))
            else:
                if self.instr.source.function()=='current':
                    for i in np.linspace(self.instr.source.current(),value,step):
                        self.instr.source.current(i)
                        QTest.qWait(int(0.1*1000))
                else:
                    for i in np.linspace(self.instr.source.voltage(),value,step):
                        self.instr.source.voltage(i)
                        QTest.qWait(int(0.1*1000))
    def sim_voltset(self, num, val, por, wait=.1):

        self.instr.write('main_esc')
        self.instr.write('CONN'+str(por)+', "main_esc"')
        now=float(self.instr.query('VOLT?'))
        if num==0:
            self.instr.write('VOLT '+str(val))
        else:
            swp=np.linspace(now,val,num)
            for i in range(swp.size):
                self.instr.write('VOLT '+str(swp[i]))
                QTest.qWait(int(wait*1000))
        self.instr.write('main_esc')
    
    def sim_voltsweep(self, st, va, po, wa =.1):
        value=float(va.text())
        step=float(st.text())
        port=int(po.text())
        
        self.sim_voltset(step, value, port, wa)
    
    def get_simvolt(self,port):
        self.instr.write('main_esc')
        self.instr.write('CONN'+str(port)+', "main_esc"')
        v=self.instr.query('VOLT?')
        self.instr.write('main_esc')
        return v
    
    def simoutput(self, button, port):
        self.instr.write('main_esc')
        self.instr.write('CONN'+str(port)+', "main_esc"')
        on=int(self.instr.query('EXON?'))
        self.instr.write('main_esc')
        if on == 1:
            button.setText('On')    
            button.setStyleSheet("background-color: #008B45;")
        elif on == 0:
            button.setText('Off')
            button.setStyleSheet("background-color: #CD4F39;")
        else:
            pass
    def togglesimoutput(self, button, portl):
        port=portl.text()
        self.instr.write('main_esc')
        self.instr.write('CONN'+port+', "main_esc"')
        on=int(self.instr.query('EXON?'))
        if on == 1:
            self.instr.write('OPOF')
            button.setText('Off')    
            button.setStyleSheet("background-color: #CD4F39;")
        elif on == 0:
            self.instr.write('OPON')
            button.setText('On')
            button.setStyleSheet("background-color: #008B45;")
        else:
            pass
        
        self.instr.write('main_esc')
                        
    def setB(self, Bsetp, Bramp):
        ramp = float(Bramp.text())
        setpoint = float(Bsetp.text())
        if ramp>.035:
            ramp=.035
        if setpoint>9:
            setpoint=9
        elif setpoint<-9:
            setpoint=-9
        
        htr_stat = self.instr.pers_htr_state()
        if htr_stat == 1:
            self.instr.current_ramp_rate(ramp)
            self.instr.field_ramp_target(setpoint)
        elif htr_stat == 0:
            warning = QMessageBox()
            warning.setIcon(QMessageBox.Information)
            warning.setWindowTitle("Warning")
            warning.setText('Heater if OFF.\nCannot sweep to target field.')
            warning.setStandardButtons(QMessageBox.Ok)
            warning.exec()
        else:
            pass
        #htr_stat = self.instr.query('READ:DEV:GRPZ:PSU:SIG:SWHT').split(':')[6]
        ramp = None
        setpoint = None
    def htrOn(self):
        self.instr.htr_on()
    def htrOff(self):
        self.instr.htr_off()
    def getBTarget(self):
        return self.instr.current_ramp_target()
    def getBRate(self):
        return self.instr.current_ramp_rate()
    
    def checkHtrStatus(self, box):
        htr_stat = self.instr.pers_htr_state()
        if htr_stat == 1:
            box.setText('On')    
            box.setStyleSheet("background-color: #008B45;")
        elif htr_stat == 0:
            box.setText('Off')
            box.setStyleSheet("background-color: #CD4F39;")
        else:
            pass
    
    def Btozero(self):
        self.instr.field_ramp_target(0)
        
    def setT(self, Tsetp, Tramp, htrrange):
        ramp = float(Tramp.text())
        setpoint = float(Tsetp.text())
        rng=htrrange.currentText()
        self.instr.heater_range_1= rng 
        self.instr.heater_range_2=rng
        self.instr.ramp_rate_1=ramp
        self.instr.ramp_rate_2=ramp
        self.instr.setpoint_1=setpoint
        self.instr.setpoint_2=setpoint
    
    def setRotate(self,axis,angle,frequency,amplitude,button):
        f=float(frequency.text())
        amp=float(amplitude.text())
        ang=float(angle.text())
        
        if amp>60:
            amp=60
            amplitude.setText(60)
        elif amp<0:
            amp=0
            amplitude.setText(0)
        
        self.instr.setAmplitude(axis,amp)
        self.instr.setFrequency(axis,f)
        self.instr.setAxisOutput(axis,1,0)
        self.instr.setTargetRange(axis,0.1)
        self.instr.setTargetPosition(axis, ang)
        self.instr.startAutoMove(axis,1,0)
        button.setStyleSheet("background-color: #008B45;")
        
    def checkCap(self, axis0box, axis1box):
        cap0=self.instr.measureCapacitance(0)*1e9
        cap1=self.instr.measureCapacitance(1)*1e9
        axis0box.setText("{:.0f}".format(cap0))
        axis1box.setText("{:.0f}".format(cap1))

    def checkGround(self, thetabutton, phibutton):
        if self.instr.getAxisStatus(0)[1]:
            thetabutton.setStyleSheet("background-color: #008B45;")
        else:
            thetabutton.setStyleSheet("background-color: #CD4F39;")
        if self.instr.getAxisStatus(1)[1]:
            phibutton.setStyleSheet("background-color: #008B45;")
        else:
            phibutton.setStyleSheet("background-color: #CD4F39;")
    
    def groundAxis(self,axis, button):
        self.instr.setAxisOutput(axis,0,0)
        button.setStyleSheet("background-color: #CD4F39;")
        