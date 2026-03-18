# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 13:59:25 2021

@author: Jordan
"""
import ast
import numpy as np
from qcodes.instrument_drivers.stanford_research.SR830 import SR830
from qcodes.instrument_drivers.stanford_research.SR860 import SR860
from qcodes.instrument_drivers.yokogawa.GS200 import GS200
from qcodes.instrument_drivers.tektronix.Keithley_2400 import Keithley_2400
from qcodes.instrument_drivers.tektronix.Keithley_2450 import Keithley2450
import pyvisa as visa
from pymeasure.instruments.signalrecovery.dsp7265 import DSP7265
from PyQt5.QtCore import QTimer



rm = visa.ResourceManager()
# from lakeshore331_test import LakeShore331
# from lakeshore_625_magnet_driver import Model_625

import os
from datetime import datetime
from PyQt5.QtWidgets import (QComboBox, 
        QGridLayout, QLabel, QLineEdit,
        QPushButton, QCheckBox, QFileDialog, QMessageBox, QDoubleSpinBox)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtTest import QTest

class DSP7265_inst:
    ch_name=['X','Y','R','P','DAC1','DAC2','DAC3','DAC4']
    fields = ['ch1 display','ch2 display','Frequency','Amplitude','Time constant','AC gain','Increase sensitivity','Decrease sensitivity','Sweep mode','Sweep start (Hz or V rms)','Sweep stop (Hz or V rms)','Number of intervals','Wait time (s)']
    display_fields = ['Live frequency','Live amplitude','Live time constant','Live AC gain','Live sensitivity','Error status','Status byte']
    ch1Display = ['X', 'R']
    ch2Display = ['Y', 'Phase']
    lockin_tc_val = ['10e-6','20e-6','40e-6','80e-6','160e-6','320e-6','640e-6','5e-3','10e-3','20e-3','50e-3','100e-3','200e-3','500e-3','1','2','5','10','20','50','100','200','500','1e3','2e3','5e3','10e3','20e3','50e3','100e3']
    lockin_gain_val = ['0','10','20','30','40','50','60','70','80','90']
    sweep_mode = ['amplitude','frequency']
    def __init__(self, name, address, channels):
        self.name=name
        self.gpib=address
        self.ch=ast.literal_eval(channels)
        self.instr=DSP7265(address)
        self.parameters = [self.instr.frequency, self.instr.voltage, self.instr.time_constant, self.instr.ac_gain, self.instr.sensitivity]
        self.log_timer = None       # QTimer used by the logger tab
        self.log_file  = None       # open file handle while logging
        
        print('Connected to DSP7265 ('+name+')!')
        
    def measure(self):
        msmt=[]
        if self.ch[0:3]==[True,True,False,False]:
            val=(self.instr.x, self.instr.y)
            msmt=[str(val[0]),str(val[1])]
        elif self.ch[0:3]==[False,False,True,True]:
            val=(self.instr.mag, self.instr.phase)
            msmt=[str(val[0]),str(val[1])]
        elif self.ch[0:3]==[True,False,False,True]:
            val=(self.instr.x, self.instr.phase)
            msmt=[str(val[0]),str(val[1])]
        else:
            if self.ch[0]:
                msmt.append(str(self.instr.x))
            if self.ch[1]:
                msmt.append(str(self.instr.y))
            if self.ch[2]:
                msmt.append(str(self.instr.mag))
            if self.ch[3]:
                msmt.append(str(self.instr.phase))
            if self.ch[4]:
                msmt.append(str(self.instr.dac1))
            if self.ch[5]:
                msmt.append(str(self.instr.dac2))
            if self.ch[6]:
                msmt.append(str(self.instr.dac3))
            if self.ch[7]:
                msmt.append(str(self.instr.dac4))
        return msmt
    
    def header(self):
        hdr=[]
        for ind in range(len(self.ch)):
            if self.ch[ind]:
                hdr.append(self.name+'_'+self.ch_name[ind])
        return hdr
    
    def control_GUI(self, frame): #Create the apearence for dsp7265
        j=0
        label={}
        for i, f in enumerate(self.fields):
            if i in range(len(self.fields)):
                label[f] = QLabel(f)
            else:
                label[f] = None
            j+=1
        reference_entry = QCheckBox()
        ch1display_entry = QComboBox()
        ch1display_entry.addItems(self.ch1Display)
        ch2display_entry = QComboBox()
        ch2display_entry.addItems(self.ch2Display)
        freq_entry = QLineEdit(frame)
        #freq_entry.setDisabled(True)
        amp_entry = QLineEdit(frame)
        #amp_entry.setDisabled(True)
        reference_entry.toggled.connect(freq_entry.setEnabled)
        reference_entry.toggled.connect(amp_entry.setEnabled)
        tc_entry = QComboBox()
        tc_entry.addItems(self.lockin_tc_val)
        gain_entry = QComboBox()
        gain_entry.addItems(self.lockin_gain_val)
        sweep_var_entry = QComboBox()
        sweep_var_entry.addItems(self.sweep_mode)
        sweep_start_entry = QLineEdit(frame)
        #sweep_start_entry.setDisabled(True)
        sweep_stop_entry = QLineEdit(frame)
        #sweep_stop_entry.setDisabled(True)
        sweep_pts_entry = QLineEdit(frame)
        #sweep_pts_entry.setDisabled(True)
        sweep_wait_entry = QLineEdit(frame)
        #sweep_wait_entry.setDisabled(True)
        sweep_trigger_button = QPushButton("Start sweep")
        sweep_trigger_button.clicked.connect(
            lambda: self.sweep_val(
                sweep_var_entry.currentText(),     # «frequency» / «amplitude»
                sweep_start_entry.text(),          # raw text  (can be blank)
                float(sweep_stop_entry.text()),    # keep numeric conversion
                int(sweep_pts_entry.text()),
                float(sweep_wait_entry.text())
            )
        )
        upsens_button = QPushButton('Increase sensitivity')
        upsens_button.clicked.connect(lambda: self.inc_sens_lockin())
        downsens_button = QPushButton('Decrease sensitivity')
        downsens_button.clicked.connect(lambda: self.dec_sens_lockin())
        set_button = QPushButton('Set lockin parameters')
        set_button.clicked.connect(lambda: self.set_lockin_param(reference_entry,ch1display_entry,ch2display_entry,freq_entry,amp_entry,tc_entry,gain_entry))
        set_button.clicked.connect(lambda: QTest.qWait(int(100)))
        set_button.clicked.connect(lambda: self.update_display())
        autophase_button = QPushButton('Auto phase')
        autophase_button.clicked.connect(lambda: self.instr.auto_phase())
        shutdown_button = QPushButton('Shut down')
        shutdown_button.clicked.connect(lambda: self.instr.shutdown())
        #autogain_button = QPushButton("Auto gain")
        #autogain_button.setToolTip("Let the lock‑in choose a suitable gain")
        #autogain_button.clicked.connect(self.auto_gain)
        
        layout = QGridLayout()
        for i, f in enumerate(self.fields):
            if i in range(len(self.fields)):
                layout.addWidget(label[f], i, 0, 1, 1)
        #layout.addWidget(reference_entry, 19, 1, 1, 1)
        layout.addWidget(ch1display_entry, 0, 1, 1, 1)
        layout.addWidget(ch2display_entry, 1, 1, 1, 1)
        layout.addWidget(freq_entry, 2, 1, 1, 1)
        layout.addWidget(amp_entry, 3, 1, 1, 1)
        layout.addWidget(tc_entry, 4, 1, 1, 1)
        layout.addWidget(gain_entry, 5, 1, 1, 1)
        layout.addWidget(upsens_button, 6, 0, 1, 1)
        layout.addWidget(downsens_button, 6, 1, 1, 1)
        layout.addWidget(set_button, 7, 0, 1, 1)
        layout.addWidget(autophase_button, 7, 1, 1, 1)
        layout.addWidget(sweep_var_entry, 8, 1, 1, 1)
        layout.addWidget(sweep_start_entry, 9, 1, 1, 1)
        layout.addWidget(sweep_stop_entry, 10, 1, 1, 1)
        layout.addWidget(sweep_pts_entry, 11, 1, 1, 1)
        layout.addWidget(sweep_wait_entry, 12, 1, 1, 1)
        layout.addWidget(sweep_trigger_button, 13, 1, 1, 1)
        layout.addWidget(shutdown_button, 13, 0, 1, 1)
        #layout.addWidget(autogain_button, 14, 0, 1, 1)

        layout.setRowStretch(j+3, 2)
        
        frame.setLayout(layout)
    def display_GUI(self, frame):
        # ----- create labels and keep references -----
        self.live_freq_display = QLabel()
        self.live_amp_display = QLabel()
        self.live_tc_display = QLabel()
        self.live_gain_display = QLabel()
        self.live_sens_display = QLabel()

        # NEW – error line
        self.live_err_display = QLabel()  

        # NEW  – status‑byte line
        self.live_status_display = QLabel()

        # call once to populate the labels with current values
        self.update_display()

        # ----- static headings -----
        layout = QGridLayout()
        for row, heading in enumerate(self.display_fields):
            layout.addWidget(QLabel(heading), row, 0)

        # ----- live value widgets -----
        layout.addWidget(self.live_freq_display, 0, 1)
        layout.addWidget(self.live_amp_display,  1, 1)
        layout.addWidget(self.live_tc_display,   2, 1)
        layout.addWidget(self.live_gain_display, 3, 1)
        layout.addWidget(self.live_sens_display, 4, 1)
        layout.addWidget(self.live_err_display, 5, 1)
        layout.addWidget(self.live_status_display, 6, 1)

        # ----- refresh timer -----
        frame.timer = QTimer(frame)
        frame.timer.timeout.connect(self.update_display)   # only this one call is needed
        frame.timer.start(1000)  # ms

        frame.setLayout(layout)

    def logger_GUI(self, frame):
        """
        Builds the 'Data Logger' tab.
        Lets the user choose a file and sampling time, then logs the five
        live parameters that update_display() maintains.
        """
        # -------- widgets ------------------------------------------------
        file_label   = QLabel("Output file:")
        self.file_box = QLineEdit(
            os.path.join(os.getcwd(), f"{self.name}_log.txt"))
        browse_btn   = QPushButton("Browse…")

        interval_label = QLabel("Sampling interval (s):")
        self.interval_box = QDoubleSpinBox()
        self.interval_box.setDecimals(2)
        self.interval_box.setRange(0.1, 3600.0)
        self.interval_box.setValue(1.0)

        self.start_btn = QPushButton("Start")
        self.stop_btn  = QPushButton("Stop")
        self.stop_btn.setEnabled(False)

        status_label = QLabel("Status:")
        self.status_value = QLabel("Idle")

        # -------- layout -------------------------------------------------
        layout = QGridLayout()
        layout.addWidget(file_label,        0, 0)
        layout.addWidget(self.file_box,     0, 1)
        layout.addWidget(browse_btn,        0, 2)

        layout.addWidget(interval_label,    1, 0)
        layout.addWidget(self.interval_box, 1, 1)

        layout.addWidget(self.start_btn,    2, 0)
        layout.addWidget(self.stop_btn,     2, 1)

        layout.addWidget(status_label,      3, 0)
        layout.addWidget(self.status_value, 3, 1)

        frame.setLayout(layout)

        # -------- behaviour ---------------------------------------------
        browse_btn.clicked.connect(
            lambda: self._browse_for_file(frame))

        self.start_btn.clicked.connect(
            lambda: self._start_logging(frame))

        self.stop_btn.clicked.connect(
            self._stop_logging)
    # ------------------------------------------------------------------
    # helper slots -------------------------------------------------------
    def _browse_for_file(self, parent):
        fname, _ = QFileDialog.getSaveFileName(
            parent, "Choose log file", self.file_box.text(),
            "Text files (*.txt);;All files (*)")
        if fname:
            self.file_box.setText(fname)

    def _start_logging(self, parent):
        # validate interval --------------------------------------------
        interval = self.interval_box.value()
        if interval <= 0:
            QMessageBox.warning(parent, "Invalid interval",
                                "Sampling time must be > 0 s.")
            return

        # open / create file -------------------------------------------
        path = self.file_box.text()
        try:
            new_file = not os.path.exists(path) or os.path.getsize(path) == 0
            self.log_file = open(path, "a", buffering=1)   # line-buffered
            if new_file:
                header = ("timestamp,frequency_Hz,amplitude_Vrms,"
                          "timeConstant_s,ACgain,sensitivity\n")
                self.log_file.write(header)
        except OSError as err:
            QMessageBox.critical(parent, "File error",
                                 f"Cannot open '{path}':\n{err}")
            return

        # prepare timer -------------------------------------------------
        if self.log_timer is None:
            self.log_timer = QTimer(parent)
            self.log_timer.timeout.connect(self._write_log_line)

        self.log_timer.start(int(interval * 1000))

        # update GUI ----------------------------------------------------
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.interval_box.setEnabled(False)
        self.file_box.setEnabled(False)
        self.status_value.setText("Logging…")

    def _stop_logging(self):
        if self.log_timer is not None:
            self.log_timer.stop()
        if self.log_file is not None:
            self.log_file.close()
            self.log_file = None

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.interval_box.setEnabled(True)
        self.file_box.setEnabled(True)
        self.status_value.setText("Idle")

    def _write_log_line(self):
        """
        Called by the QTimer every interval.
        Grabs fresh parameters, formats one line, appends to file.
        """
        # refresh internal cache so we log current values
        self.update_display()

        if self.log_file is None:        # shouldn't happen, but be safe
            return

        now = datetime.now().isoformat(timespec='seconds')
        line = (f"{now},{self.parameters[0]},{self.parameters[1]},"
                f"{self.parameters[2]},{self.parameters[3]},"
                f"{self.parameters[4]}\n")
        try:
            self.log_file.write(line)
        except OSError:
            # stop on write error
            self._stop_logging()

    def set_lockin_param(self,ref,display1,display2,freq,amp,tc,gain):
        """
        if self.instr.voltage < 0.004:
            amp_start = 0.004
        elif self.instr.voltage > 5:
            amp_start = 5
        else:
            amp_start = self.instr.voltage
        """
        """
        if ref.isChecked()==True:
            self.instr.reference_source('internal')
        else:
            self.instr.reference_source('external')
        self.instr.ch1_display(display1.currentText())
        self.instr.ch2_display(display2.currentText())
        """
        amp_start = self.instr.voltage
        if len(freq.text()) == 0:
            pass
        else:
            self.instr.frequency = float(freq.text())
        if len(amp.text()) == 0:
            pass
        else:
            if float(amp.text())>5:
                self.instr.voltage = 5
            #elif float(amp.text())<0.004:
                #self.instr.voltage = 0.004
            else:
                self.instr.voltage = float(amp.text())
            L = np.linspace(amp_start,self.instr.voltage, 21)
            for amp in L:
                self.instr.voltage = amp
                QTest.qWait(int(0.1*1000))
        self.instr.time_constant = float(tc.currentText())
        print('Time constant is set to ' + str(self.instr.time_constant) + ' s')
        self.instr.ac_gain = int(gain.currentText())
        if int(self.instr.ac_gain) != int(gain.currentText()):
            print("AC gain setting failed! Please decrease the sensitivity below the input limit.")
        else:
            print('AC gain is set to ' + str(self.instr.ac_gain) + ' dB')
    
    #sensitivity_values_str = ['2e-9','5e-9','1e-8','2e-8','5e-8','1e-7','2e-7','5e-7','1e-6','2e-6','5e-6','1e-5','2e-5','5e-5','1e-4','2e-4','5e-4','1e-3','2e-3','5e-3','0.01','0.02','0.05','0.1','0.2','0.5','1']
    #sensitivity_values_flt = [float(i) for i in sensitivity_values_str]
                
    def inc_sens_lockin(self):
        sensitivity_values_str = ['2e-9','5e-9','1e-8','2e-8','5e-8','1e-7','2e-7','5e-7','1e-6','2e-6','5e-6','1e-5','2e-5','5e-5','1e-4','2e-4','5e-4','1e-3','2e-3','5e-3','0.01','0.02','0.05','0.1','0.2','0.5','1']
        sensitivity_values_flt = [float(i) for i in sensitivity_values_str]
        if self.instr.sensitivity == 1:
            print("Oops! Maximum sensitivity reached!")
        else:
            idx = sensitivity_values_flt.index(self.instr.sensitivity)
            self.instr.sensitivity = sensitivity_values_flt[idx+1]
        print('Sensitivity set to ' + str(self.instr.sensitivity))
        
    def dec_sens_lockin(self):
        sensitivity_values_str = ['2e-9','5e-9','1e-8','2e-8','5e-8','1e-7','2e-7','5e-7','1e-6','2e-6','5e-6','1e-5','2e-5','5e-5','1e-4','2e-4','5e-4','1e-3','2e-3','5e-3','0.01','0.02','0.05','0.1','0.2','0.5','1']
        sensitivity_values_flt = [float(i) for i in sensitivity_values_str]
        if self.instr.sensitivity == 2e-9:
            print("Oops! Minimum sensitivity reached!")
        else:
            idx = sensitivity_values_flt.index(self.instr.sensitivity)
            self.instr.sensitivity = sensitivity_values_flt[idx-1]
        print('Sensitivity set to ' + str(self.instr.sensitivity) +" V")
    
    def set_val(self, var, val):
        if var == 'frequency':
            self.instr.frequency = val 
        elif var == 'amplitude':
            self.instr.voltage = val
    
    def now_at(self, var):
        if var == 'frequency':
            return self.instr.frequency
        elif var == 'amplitude':
            return self.instr.voltage
    
    def sweep_val(self, mode, start, stop, n_pts, wait, *, callback=None):
        """
        Sweep *mode* ('frequency' or 'amplitude') from *start* to *stop*
        using *n_pts* points and pausing *wait* [s] between updates.

        • If *start* is ``None`` **or** is ``math.nan`` the sweep begins at
        the instrument’s current value for that mode.

        • *stop* and *n_pts* must be finite numbers.
        ``n_pts`` ≥ 1; if it equals 1 the instrument is simply set to
        *start* (or its current value).

        • *callback* (val, idx, n_pts) is invoked after each point.

        The method is fully compatible with the trigger‑button lambda shown
        above.
        """
        import math, time
        from PyQt5.QtCore import QCoreApplication

        # ── validate & normalise the mode ──────────────────────────
        mode = mode.strip().lower()
        if mode not in ("frequency", "amplitude"):
            raise ValueError("sweep_val supports only 'frequency' or "
                            "'amplitude', not {!r}".format(mode))

        # helper – convert GUI input to float, fallback to current value
        def _default_if_blank(value, current):
            """
            Return *current* if *value* is None **or** an empty / whitespace
            string.  Otherwise convert *value* to float.
            """
            if value is None:
                return current
            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    return current
                return float(value)
            # already numeric
            return float(value)

        # ── fetch current instrument value for this mode ───────────
        if mode == "frequency":
            current_val = self.instr.frequency
            set_func    = lambda v: setattr(self.instr, "frequency", v)
        else:                       # 'amplitude'
            current_val = self.instr.voltage
            set_func    = lambda v: setattr(self.instr, "voltage", v)

        # ── resolve parameters (auto‑fallback for *start*) ─────────
        start = _default_if_blank(start, current_val)
        stop  = float(stop)
        n_pts = int(n_pts)
        wait  = max(float(wait), 0.0)        # negative wait makes no sense

        if n_pts < 1:
            raise ValueError("n_pts must be at least 1")

        # Single‑point “sweep”: just set the value and return
        if n_pts == 1:
            set_func(start)
            if callback:
                callback(start, 0, 1)
            return

        step = (stop - start) / (n_pts - 1)

        # ── main sweep loop ────────────────────────────────────────
        for idx in range(n_pts):
            val = start + idx * step
            set_func(val)

            # keep the Qt event loop alive so the GUI never freezes
            QCoreApplication.processEvents()

            if callback:
                callback(val, idx, n_pts)

            if idx < n_pts - 1 and wait:
                time.sleep(wait)
    """
    def auto_gain(self):
        '''
        Trigger the lock‑in's automatic gain routine, then refresh the live display. Compatible with both new and old PyMeasure drivers.
        '''
        import time
        from PyQt5.QtCore import QCoreApplication

        try:
            # Newer PyMeasure: auto_gain() may return a LIST
            result = self.instr.auto_gain

            # Normalise the driver's return so we can ignore it safely
            if isinstance(result, (list, tuple)):
                result_flag = int(result[0])
            else:
                result_flag = int(result)

            # Optional: you could inspect result_flag here if desired
            _ = result_flag

        except (AttributeError, TypeError, ValueError):
            # • AttributeError → driver lacks auto_gain()
            # • TypeError / ValueError → buggy return format (your crash)
            #
            #  Fall back to the raw SCPI command ('AGAN' in the SRS manual).
            self.instr.write("AGAN")

        # Give the instrument a brief moment, then refresh GUI
        QCoreApplication.processEvents()
        time.sleep(0.2)
        self.update_display()
    """

    def update_display(self):
        """
        Refresh the on‑screen values.  Called by the QTimer every second.
        """
        # ----- numeric parameters (unchanged part) -----
        self.parameters = [
            self.instr.frequency,
            self.instr.voltage,
            self.instr.time_constant,
            self.instr.ac_gain,
            self.instr.sensitivity,
        ]

        self.live_freq_display.setText(f"{self.parameters[0]:.6g} Hz")
        self.live_amp_display.setText(f"{self.parameters[1]:.4g} V₍rms₎")
        self.live_tc_display.setText(f"{self.parameters[2]:.3g} s")
        self.live_gain_display.setText(str(self.parameters[3])+" dB")
        self.live_sens_display.setText(str(self.parameters[4])+" V")

        # ----- error handling (NEW) --------------------
        try:
            errors = self.instr.check_errors()     # PyMeasure helper
            if errors:
                code, msg = errors[-1]            # show the most recent
                self.live_err_display.setText(f"{code}: {msg}")
            else:
                self.live_err_display.setText("No error")
        except (NotImplementedError, AttributeError):
            # Driver doesn’t support SCPI error queries
            self.live_err_display.setText("n/a")

        # ---------- status‑byte line (NEW) ----------
        try:
            # PyMeasure ≥ 0.12 offers a helper property
            stb = self.instr.status

        except AttributeError:
            # Older driver: manual query returns "+10019,+02761"
            raw = self.instr.ask("*STB?")        # or "STB?" on some firmware
            # keep only the first signed integer
            first_word = raw.split(",")[0]
            stb = int(first_word) & 0xFF         # mask to one byte

        # Show in both decimal & hex
        self.live_status_display.setText(f"{stb}  (0x{stb:02X})")




    """
    def set_freq(self, f):
        self.instr.frequency = float(f)
    """

class SR830_inst:
    ch_name=['X','Y','R','P','AUX_IN_1','AUX_IN_2','AUX_IN_3','AUX_IN_4']
    fields = ['Internal Reference','ch1 display','ch2 display','Frequency','Amplitude','Time constant','Increase sensitivity','Decrease sensitivity']
    ch1Display = ['X', 'R']
    ch2Display = ['Y', 'Phase']
    lockin_tc_val = ['10e-6','30e-6','100e-6','300e-6','1e-3','3e-3','10e-3','30e-3','100e-3','300e-3','1','3','10','30','100','300','1e3','3e3','10e3','30e3']
    def __init__(self, name, address, channels):
        self.name=name
        self.gpib=address
        self.ch=ast.literal_eval(channels)
        self.instr=SR830(name, address)
        
        print('Connected to SR830 ('+name+')!')
        
    def measure(self):        
        val=[]
        if self.ch[0]:
            val.append('x')
        if self.ch[1]:
            val.append('y')
        if self.ch[2]:
            val.append('r')
        if self.ch[3]:
            val.append('p')
        if self.ch[4]:
            val.append('aux1')
        if self.ch[5]:
            val.append('aux2')
        if self.ch[6]:
            val.append('aux3')
        if self.ch[7]:
            val.append('aux4')
        msmt=list(self.instr.snap(*val))
        msmt=[str(msmt) for msmt in msmt]
        return msmt
    
    def header(self):
        hdr=[]
        for ind in range(len(self.ch)):
            if self.ch[ind]:
                hdr.append(self.name+'_'+self.ch_name[ind])
        return hdr
    def control_GUI(self, frame): #Create the apearence for lockins (830 and 860)
        j=0
        label={}
        for i, f in enumerate(self.fields):
            if i in range(6):
                label[f] = QLabel(f)
            else:
                label[f] = None
            j+=1
        reference_entry = QCheckBox()
        ch1display_entry = QComboBox()
        ch1display_entry.addItems(self.ch1Display)
        ch2display_entry = QComboBox()
        ch2display_entry.addItems(self.ch2Display)
        freq_entry = QLineEdit(frame)
        freq_entry.setDisabled(True)
        amp_entry = QLineEdit(frame)
        amp_entry.setDisabled(True)
        reference_entry.toggled.connect(freq_entry.setEnabled)
        reference_entry.toggled.connect(amp_entry.setEnabled)
        tc_entry = QComboBox()
        tc_entry.addItems(self.lockin_tc_val)
        upsens_button = QPushButton('Increase sensitivity')
        upsens_button.clicked.connect(lambda: self.inc_sens_lockin())
        downsens_button = QPushButton('Decrease sensitivity')
        downsens_button.clicked.connect(lambda: self.dec_sens_lockin())
        set_button = QPushButton('Set lockin parameters')
        set_button.clicked.connect(lambda: self.set_lockin_param(reference_entry,ch1display_entry,ch2display_entry,freq_entry,amp_entry,tc_entry))
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
        frame.setLayout(layout)
    def set_lockin_param(self,ref,display1,display2,freq,amp,tc):
        if self.instr.amplitude() < 0.004:
            amp_start = 0.004
        elif self.instr.amplitude() > 5:
            amp_start = 5
        else:
            amp_start = self.instr.amplitude()
        if ref.isChecked()==True:
            self.instr.reference_source('internal')
        else:
            self.instr.reference_source('external')
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
    def set_freq(self, f):
        self.instr.frequency(float(f))

class SR860_inst:
    ch_name=['X','Y','R','P']
    def __init__(self, name, address, channels):
        self.name=name
        self.gpib=address
        self.ch=ast.literal_eval(channels)
        self.instr=SR860(name, address)        
        
        print('Connected to SR860 ('+name+')!')
        
    def measure(self):
        msmt=[]
#        pt = self.instr.get_values('X','Y','R','P')
        if self.ch==[True,True,False,False]:
            val=self.instr.get_values('X','Y')
            msmt=[str(val[0]),str(val[1])]
        elif self.ch==[False,False,True,True]:
            val=self.instr.get_values('R','P')
            msmt=[str(val[0]),str(val[1])]
        elif self.ch==[True,False,False,True]:
            val=self.instr.get_values('X','P')
            msmt=[str(val[0]),str(val[1])]
        else:
            if self.ch[0]:
                msmt.append(str(self.instr.X()))
            if self.ch[1]:
                msmt.append(str(self.instr.Y()))
            if self.ch[2]:
                msmt.append(str(self.instr.R()))
            if self.ch[3]:
                msmt.append(str(self.instr.P()))
        return msmt

    def header(self):
        hdr=[]
        for ind in range(len(self.ch)):
            if self.ch[ind]:
                hdr.append(self.name+'_'+self.ch_name[ind])
        return hdr

class K2400_inst:
    ch_name=['V','I']
    KGUI_field = ['Disable','Output', 'Mode', 'Compliance', 'Range', 'Sweep To']
    keithley_range = ['--VOLTAGE MODE--','200e-3','2','20','200','--CURRENT MODE--','1e-6','10e-6','100e-6','1e-3','10e-3','100e-3','1']
    keithley_comp = ['--VOLTAGE MODE--','1.05e-6','10.5e-6', '105e-6','1.05e-3', '10.5e-3', '105e-3', '1.05','--CURRENT MODE--','210e-3','2.1','21','210']
    K_field = ['Disable','Output', 'Mode', 'Compliance', 'Range', 'Sweep To']
    
    def __init__(self, name, address, channels):
        self.name=name
        self.gpib=address
        self.ch=ast.literal_eval(channels)
        self.instr=Keithley_2400(name, address)        
        self.param_K1 = [self.instr.output(),str(self.instr.mode())]
        print('Connected to K2400 ('+name+')!')
        self.val=self.now_at()
        
    def measure(self):
        msmt=[]
        if self.ch[0]:
            # msmt.append(str(self.instr.volt()))
            msmt.append(str(self.val))
        if self.ch[1]:
            msmt.append(str(self.instr.curr()))
        return msmt

    def header(self):
        hdr=[]
        for ind in range(len(self.ch)):
            if self.ch[ind]:
                hdr.append(self.name+'_'+self.ch_name[ind])
        return hdr
    
    def set_val(self, val, mode=0): #Make compatible with current
        if mode==0:
            if self.instr.mode()=='CURR':
                self.instr.curr(val)
            else:
                self.instr.volt(val)
                
        elif mode==1:
            self.instr.volt(val)
        elif mode==2:
            self.instr.curr(val)
        self.val=val
    def now_at(self, mode=0):
        if mode==0:
            if self.instr.mode()=='CURR':
                return self.instr.curr()
            else:
                return self.instr.volt()
        elif mode==1:
            return self.instr.volt()
        elif mode==2:
            return self.instr.curr()
    
    # def sweep_val(self,val, step, rate):
    #     if self.instr.mode()=='CURR':
    #         m=2
    #     else:
    #         m=1
    #     v0=self.now_at(mode=m)
        
    #     num=int(abs((val-v0)/step)+1)
    #     sweep=np.linspace(v0,val,num)
    #     for v in sweep:
    #         self.set_val(v, mode=m)
    #     self.set_val(val, mode=m)
    def sweep_val(self,val, pts, wait):
        if self.instr.mode()=='CURR':
            m=2
        else:
            m=1
        v0=self.now_at(mode=m)
        
        sweep=np.linspace(v0,val,pts)
        for v in sweep:
            self.set_val(v, mode=m)
            QTest.qWait(int(wait*1000))
        self.set_val(val, mode=m)
    
    def control_GUI(self, frame):#Apearence for Keithley control panel
        j=0
        label={}
        for i, f in enumerate(self.KGUI_field):
            label[f] = QLabel(f)
            j+=1
        protec_check = QCheckBox()    
        protec_check.setChecked(True)
        protec_button = None
        
        out_entry = None
        out_button = QPushButton('ON' if self.param_K1[0] == True else 'OFF')
        out_button.setEnabled(False)
        protec_check.toggled.connect(out_button.setDisabled)
        out_button.setStyleSheet("background-color: #008B45;" if self.param_K1[0] == True else "background-color: #CD4F39;")
        out_button.clicked.connect(lambda: self.set_output(out_button))
            
        mode_entry = None
        mode_button = QPushButton('VOLT' if self.param_K1[1] in ['VOLT','voltage'] else 'CURR')
        mode_button.setEnabled(False)
        protec_check.toggled.connect(mode_button.setDisabled)
        mode_button.clicked.connect(lambda: self.set_mode(mode_button,out_button))

        comp_entry = QComboBox()
        comp_entry.addItems(self.keithley_comp)
        # if instr.get_idn()['model'] == '2400':
        #     comp_entry.addItems(self.keithley_comp)
        # else:
        #     comp_entry.addItems(self.keithley2450_comp)
        comp_button = QPushButton('Set')
        comp_button.clicked.connect(lambda: self.set_compliance(comp_entry))
        
        range_entry = QComboBox()
        range_entry.addItems(self.keithley_range)
        range_button = QPushButton('Set')
        range_button.clicked.connect(lambda: self.set_range(range_entry))
        
        sweep_entry = QLineEdit(frame)
        sweepTime_entry = QLineEdit(frame)
        sweep_button = QPushButton('Set')
        sweep_button.clicked.connect(lambda: self.sweep_to(sweepTime_entry,sweep_entry, sweep_button))
            
        layout = QGridLayout()
        for i, f in enumerate(self.K_field):
            layout.addWidget(label[f], i, 0, 1, 1)
        layout.addWidget(protec_check, 0, 1, 1, 2)
        layout.addWidget(protec_button, 0, 3, 1, 1)
        layout.addWidget(out_entry, 1, 1, 1, 2)
        layout.addWidget(out_button, 1, 3, 1, 1)
        layout.addWidget(mode_entry, 2, 1, 1, 2)
        layout.addWidget(mode_button, 2, 3, 1, 1)
        layout.addWidget(comp_entry, 3, 1, 1, 2)
        layout.addWidget(comp_button, 3, 3, 1, 1)
        layout.addWidget(range_entry, 4, 1, 1, 2)
        layout.addWidget(range_button, 4, 3, 1, 1)
        layout.addWidget(QLabel('value'), 5, 1, 1, 1)
        layout.addWidget(QLabel('number of points'), 5, 2, 1, 1)
        layout.addWidget(sweep_entry, 6, 1, 1, 1)
        layout.addWidget(sweepTime_entry, 6, 2, 1, 1)
        layout.addWidget(sweep_button, 6, 3, 1, 1)

        layout.setRowStretch(j+2, 3)
        frame.setLayout(layout)
    def set_output(self,button):
        if self.instr.output()==True:
            self.instr.output(False)
            button.setText('OFF')
            button.setStyleSheet("background-color: #CD4F39;")
        else:
            self.instr.output(True)
            button.setText('ON')
            button.setStyleSheet("background-color: #008B45;")
    
    def set_mode(self,val,out):
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
    # def set_read():
    #     return
    
    def set_compliance(self, val):
        value = float(val.currentText())
        if self.instr.mode() == 'CURR':
            self.instr.compliancev(value)
        else:
            self.instr.compliancei(value)
    
    def set_range(self, val):
        value = float(val.currentText())
        if self.instr.mode() == 'CURR':
            self.instr.rangei(value)
        else:
            self.instr.rangev(value)
    
    def sweep_to(self,ste,val,but):
        value = float(val.text())
        step = int(ste.text())
        but.setStyleSheet("background-color: #008B45;")
        self.sweep_val(value, step, .1)
        but.setStyleSheet("background-color: #464646;")

class K2450_inst:
    ch_name=['V','I']
    KGUI_field = ['Disable','Output', 'Mode', 'Compliance', 'Range', 'Sweep To']
    keithley2450_range = ['--VOLTAGE MODE--','20e-3','200e-3','2','20','200','--CURRENT MODE--','10e-9','100e-9','1e-6','10e-6','100e-6','1e-3','10e-3','100e-3','1']
    keithley2450_comp = ['--READ CURRENT MODE--','10e-9','100e-9','1e-6','10e-6', '100e-6','1e-3', '10e-3', '100e-3', '1','--READ VOLTAGE MODE--','210e-3','2.1','21','210']

    def __init__(self, name, address, channels):
        self.name=name
        self.gpib=address
        self.ch=ast.literal_eval(channels)
        self.instr=Keithley2450(name, address)        
        self.param_K1 = [self.instr.output_enabled(),self.instr.source.function(),self.instr.sense.function()]
        print('Connected to K2450 ('+name+')!')
        
    def measure(self):
        msmt=[]
        if self.ch[0]:
            msmt.append(self.instr.volt())
        if self.ch[1]:
            msmt.append(self.instr.curr())
        return msmt

    def header(self):
        hdr=[]
        for ind in range(len(self.ch)):
            if self.ch[ind]:
                hdr.append(self.name+'_'+self.ch_name[ind])
        return hdr
    
    def set_val(self, val, mode=0): #Make compatible with current
        if mode==0:
            if self.instr.source.function()=='current':
                self.instr.currrent(val)
            else:
                self.instr.voltage(val)
                
        elif mode==1:
            self.instr.voltage(val)
        elif mode==2:
            self.instr.current(val)
    def now_at(self, mode=0):
        if mode==0:
            if self.instr.source.function()=='current':
                return self.instr.currrent()
            else:
                return self.instr.voltage()
        elif mode==1:
            return self.instr.voltage()
        elif mode==2:
            return self.instr.current()
    
    def sweep_val(self,val, step, rate):
        if self.instr.source.function()=='current':
            m=2
        else:
            m=1
        v0=self.now_at(mode=m)
        
        num=int(abs((val-v0)/step)+1)
        sweep=np.linspace(v0,val,num)
        for v in sweep:
            self.set_val(v, mode=m)
        self.set_val(val, mode=m)
    
    def control_GUI(self, frame):#Apearence for Keithley control panel
    
        j=0
        label={}
        for i, f in enumerate(self.KGUI_field):
            label[f] = QLabel(f)
            j+=1
        protec_check = QCheckBox()    
        protec_check.setChecked(True)
        protec_button = None
        
        out_entry = None
        out_button = QPushButton('ON' if self.param_K1[0] == True else 'OFF')
        out_button.setEnabled(False)
        protec_check.toggled.connect(out_button.setDisabled)
        out_button.setStyleSheet("background-color: #008B45;" if self.param_K1[0] == True else "background-color: #CD4F39;")
        out_button.clicked.connect(lambda: self.set_output(out_button))
            
        mode_entry = None
        mode_button = QPushButton('VOLT' if self.param_K1[1] in ['VOLT','voltage'] else 'CURR')
        mode_button.setEnabled(False)
        protec_check.toggled.connect(mode_button.setDisabled)
        mode_button.clicked.connect(lambda: self.set_mode(mode_button,out_button))
        

        read_entry = None
        read_button = QPushButton('VOLT' if self.param_K1[2] in ['VOLT','voltage'] else 'CURR')
        read_button.setEnabled(False)
        protec_check.toggled.connect(read_button.setDisabled)
        read_button.clicked.connect(lambda: self.set_read(read_button))

        comp_entry = QComboBox()
        comp_entry.addItems(self.keithley_comp)
        # if instr.get_idn()['model'] == '2400':
        #     comp_entry.addItems(self.keithley_comp)
        # else:
        #     comp_entry.addItems(self.keithley2450_comp)
        comp_button = QPushButton('Set')
        comp_button.clicked.connect(lambda: self.set_compliance(comp_entry))
        
        range_entry = QComboBox()
        range_entry.addItems(self.keithley_range)
        range_button = QPushButton('Set')
        range_button.clicked.connect(lambda: self.set_range(range_entry))
        
        sweep_entry = QLineEdit(frame)
        sweepTime_entry = QLineEdit(frame)
        sweep_button = QPushButton('Set')
        sweep_button.clicked.connect(lambda: self.sweep_to(sweepTime_entry,sweep_entry))
            
        layout = QGridLayout()
        for i, f in enumerate(self.K_field):
            layout.addWidget(label[f], i, 0, 1, 1)
        layout.addWidget(protec_check, 0, 1, 1, 2)
        layout.addWidget(protec_button, 0, 3, 1, 1)
        layout.addWidget(out_entry, 1, 1, 1, 2)
        layout.addWidget(out_button, 1, 3, 1, 1)
        layout.addWidget(mode_entry, 2, 1, 1, 2)
        layout.addWidget(mode_button, 2, 3, 1, 1)
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
        frame.setLayout(layout)
    def set_output(self,button):
        if self.instr.output_enabled()==True:
            self.instr.output_enabled(False)
            button.setText('OFF')
            button.setStyleSheet("background-color: #CD4F39;")
        else:
            self.instr.output_enabled(True)
            button.setText('ON')
            button.setStyleSheet("background-color: #008B45;")
    
    def set_mode(self,val,out):
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
    
    def set_compliance(self, val):
        value = float(val.currentText())
        if self.instr.mode() == 'CURR':
            self.instr.compliancev(value)
        else:
            self.instr.compliancei(value)
    
    def set_range(self, val):
        value = float(val.currentText())
        if self.instr.mode() == 'CURR':
            self.instr.rangei(value)
        else:
            self.instr.rangev(value)
    
    def sweep_to(self,ste,val):
        value = float(val.text())
        step = float(ste.text())
        self.sweep_val(value, step, .1)
    
    def set_read(self,val):
        if self.instr.sense.function() == 'current':
            self.instr.sense.function('voltage')
            val.setText('VOLT')
        elif self.instr.sense.function() == 'voltage':
            self.instr.sense.function('current')
            val.setText('CURR')

class yoko_inst:
    ch_name=['V','I']
    Y_field = ['Disable','Output', 'Mode', 'Range', 'Sweep To']
    yoko_range=['--VOLTAGE MODE--','10e-3','100e-3','1', '10','30','--CURRENT MODE','1e-3','10e-3','100e-3','200e-3']
    def __init__(self, name, address, channels):
        self.name=name
        self.gpib=address
        self.ch=ast.literal_eval(channels)
        self.instr=GS200(name, address)      
        self.param = [str(self.instr.output()),str(self.instr.source_mode())]
        print(self.instr.voltage_range)
        # if self.param[1]=='VOLT':
        #     self.instr.voltage_range(self.instr.voltage_range)
        # elif self.param[1]=='CURR':
        #     self.instr.current_range(self.instr.current_range)
        print('Connected to Yoko ('+name+')!')
        
    def measure(self):
        msmt=[]
        if self.ch[0]:
            msmt.append(str(self.instr.voltage()))
        if self.ch[1]:
            msmt.append(str(self.instr.curreent()))
        return msmt

    def header(self):
        hdr=[]
        for ind in range(len(self.ch)):
            if self.ch[ind]:
                hdr.append(self.name+'_'+self.ch_name[ind])
        return hdr
    
    def set_output(self,val):
        if self.instr.output()=='on':
            self.instr.off()
            val.setText('OFF')
            val.setStyleSheet("background-color: #CD4F39;")
        else:
            self.instr.on()
            val.setText('ON')
            val.setStyleSheet("background-color: #008B45;")
    
    def set_val(self, val, mode=0): #Make compatible with current
        if mode==0:
            if self.instr.source_mode()=='CURR':
                self.instr.currrent(val)
            else:
                self.instr.voltage(val)
                
        elif mode==1:
            self.instr.voltage(val)
        elif mode==2:
            self.instr.current(val)
    def now_at(self, mode=0):
        if mode==0:
            if self.instr.source_mode()=='CURR':
                return self.instr.currrent()
            else:
                return self.instr.voltage()
        elif mode==1:
            return self.instr.voltage()
        elif mode==2:
            return self.instr.current()
    
    def sweep_val(self,val, pts, wait):
        
        if self.instr.source_mode()=='CURR':
            m=2
        else:
            m=1
        v0=self.now_at(mode=m)
        sweep=np.linspace(v0,val,int(pts))
        for v in sweep:
            self.set_val(v, mode=m)
            QTest.qWait(int(wait*1000))
        self.set_val(val, mode=m)

    
    def control_GUI(self, frame):#Apearence for Keithley control panel
        label={}
        j=0
        for i, f in enumerate(self.Y_field):
            label[f] = QLabel(f)
            j+=1
        protec_check = QCheckBox()    
        protec_check.setChecked(True)
        protec_button = None    
        
        out_entry = None
        out_button = QPushButton('ON' if self.param[0] == 'on' else 'OFF')
        out_button.setEnabled(False)
        protec_check.toggled.connect(out_button.setDisabled)
        out_button.setStyleSheet("background-color: #008B45;" if self.param[0] == 'on' else "background-color: #CD4F39;")
        out_button.clicked.connect(lambda: self.set_output(out_button))

        mode_entry = None
        mode_button = QPushButton('VOLT' if self.param[1]== 'VOLT' else 'CURR')
        mode_button.setEnabled(False)
        protec_check.toggled.connect(mode_button.setDisabled)
        mode_button.clicked.connect(lambda: self.set_mode(mode_button,out_button))

        range_entry = QComboBox()
        range_entry.addItems(self.yoko_range)
        range_button = QPushButton('Set')
        range_button.clicked.connect(lambda: self.set_range(range_entry))

        sweep_entry = QLineEdit(frame)
        sweepTime_entry = QLineEdit(frame)
        sweep_button = QPushButton('Set')
        sweep_button.clicked.connect(lambda: self.sweep_to(sweepTime_entry,sweep_entry,sweep_button))
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
        frame.setLayout(layout)
    
    def set_mode(self,val,out):
        if self.instr.source_mode()=='CURR':
            self.instr.source_mode('VOLT')
            val.setText('VOLT')
        else:
            self.instr.source_mode('CURR')
            val.setText('CURR')
    
    def set_compliance(self, val):
        value = float(val.currentText())
        if self.instr.mode() == 'CURR':
            self.instr.compliancev(value)
        else:
            self.instr.compliancei(value)
    
    def set_range(self, val):
        value = float(val.currentText())
        if self.instr.source_mode()=='CURR':
            self.instr.current_range(value)
        else:
            self.instr.voltage_range(value)
    
    def sweep_to(self,ste,val,but):
        value = float(val.text())
        step = float(ste.text())
        but.setStyleSheet("background-color: #008B45;")
        self.sweep_val(value, step, .1)
        but.setStyleSheet("background-color: #464646;")
        
        
    
    def set_read(self,val):
        if self.instr.sense.function() == 'current':
            self.instr.sense.function('voltage')
            val.setText('VOLT')
        elif self.instr.sense.function() == 'voltage':
            self.instr.sense.function('current')
            val.setText('CURR')

class SIM_inst:
    ch_name=['1','2','3','4','5','6','7','8']
    KGUI_field = ['Disable','Output', 'Mode', 'Compliance', 'Range', 'Sweep To']
    keithley_range = ['--VOLTAGE MODE--','200e-3','2','20','200','--CURRENT MODE--','1e-6','10e-6','100e-6','1e-3','10e-3','100e-3','1']
    keithley_comp = ['--VOLTAGE MODE--','1.05e-6','10.5e-6', '105e-6','1.05e-3', '10.5e-3', '105e-3', '1.05','--CURRENT MODE--','210e-3','2.1','21','210']
    K_field = ['Disable','Output', 'Mode', 'Compliance', 'Range', 'Sweep To']
    
    def __init__(self, name, address, channels):
        self.name=name
        self.gpib=address
        self.ch=ast.literal_eval(channels)
        self.instr = rm.open_resource(self.gpib)
        self.instr.read_termination='\r\n'
        self.instr.write_termination='\r\n'
        print(self.instr.query('*IDN?'))
        print('Connected to SIM ('+name+')!')
        self.val=self.now_at()
        
    def measure(self):
        msmt=[]
        if self.ch[0]:
            # msmt.append(str(self.instr.volt()))
            msmt.append(str(self.val))
        if self.ch[1]:
            msmt.append(str(self.instr.curr()))
        return msmt

    def header(self):
        hdr=[]
        for ind in range(len(self.ch)):
            if self.ch[ind]:
                hdr.append(self.name+'_'+self.ch_name[ind])
        return hdr
    
    def set_val(self, val, por=2): #Make compatible with current
        
        self.instr.write('main_esc')
        self.instr.write('CONN'+str(por)+', "main_esc"')
        self.instr.write('VOLT '+str(val))
        self.instr.write('main_esc')
        self.val=val

    def now_at(self, port=2):
        self.instr.write('main_esc')
        self.instr.write('CONN'+str(port)+', "main_esc"')
        v=self.instr.query('VOLT?')
        self.instr.write('main_esc')
        return v
    
    def sim_voltsweep(self, st, va, po, wa =.1):
        value=float(va.text())
        step=float(st.text())
        port=int(po.text())
        
        self.sim_voltset(step, value, port, wa)
    def sweep_val(self,val, pts, wait, port=2):
        v0=self.now_at(port=port)
        
        sweep=np.linspace(v0,val,pts)
        for v in sweep:
            self.set_val(v, por=port)
            QTest.qWait(int(wait*1000))
        self.set_val(val,por=port)
    
    def control_GUI(self, frame): #Apearence for SIM
#        simcmd=Commands(instr)
        port={}
        vset={}
        batt={}
        sweep={}
        output={}
        port_list=[]
        for i,f in enumerate(self.ch):
            if f:
                port_list.append(int(self.ch_name[i]))
#        portdefault=[2,3,4]
        layout = QGridLayout()
        for i in range(len(port_list)):
            port=QLineEdit(frame)
            port.setText(str(port_list[i]))
            vset=QLineEdit(frame)
            vset.setText(self.now_at(port_list[i]))
            step=QLineEdit(frame)
            step.setText('0.1')
            batt=QPushButton('Switch Battery')
            sweep=QPushButton('Sweep')
            output=QLineEdit('Output')
            output.setDisabled(True)
            self.check_output(output,port_list[i])
            button=QPushButton('Toggle Output')
            button.clicked.connect(lambda state, outp=output, po=port: self.toggle_output(outp,po))
            sweep.clicked.connect(lambda state, st=step,va=vset,po=port: self.sweep_to(st,va,po))
            
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
        frame.setLayout(layout)
    def check_output(self, button, port):
        self.instr.write('main_esc')
        self.instr.write('CONN'+str(port)+',"main_esc"')
        print(port)
        on=int(float(self.instr.query('EXON?')))
        self.instr.write('main_esc')
        if on == 1:
            button.setText('On')    
            button.setStyleSheet("background-color: #008B45;")
        elif on == 0:
            button.setText('Off')
            button.setStyleSheet("background-color: #CD4F39;")
        else:
            pass
    def toggle_output(self, button, portl):
        port=portl.text()
        self.instr.write('main_esc')
        self.instr.write('CONN'+port+', "main_esc"')
        on=int(float(self.instr.query('EXON?')))
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

    def set_output(self,button):
        if self.instr.output()==True:
            self.instr.output(False)
            button.setText('OFF')
            button.setStyleSheet("background-color: #CD4F39;")
        else:
            self.instr.output(True)
            button.setText('ON')
            button.setStyleSheet("background-color: #008B45;")
    
    def sweep_to(self,ste,val, por):
        value = float(val.text())
        step = int(ste.text())
        p = int(por.text())
        self.sweep_val(value, step, .1, port=p)
        

class K6221_inst:
    ch_name=['']
    fields = ['I output','NPLC']
    current=0
    def __init__(self, name, address):
        self.name=name
        self.gpib=address
        self.instr = rm.open_resource(self.gpib)
        print('Connected to Keithley 6221 ('+name+')!')
        
    def measure(self):
        msmt=[]
        msmt.append(str(self.instr.query(" SENS:DATA:LATest? ").split(',')[0]))
        # self.instr.write('SYST:COMM:SER:SEND ":SENS:DATA?"')
        # QTest.qWait(10)
        # msmt.append(str(self.instr.query('SYST:COMM:SER:ENT?').split('\n')[0]))#
        return msmt

    def header(self):
        hdr=[]
        hdr.append(self.name)
        return hdr
    
    def control_GUI(self, frame): #Create the apearence for lockins (830 and 860)
        label={}
        j=0
        for i, f in enumerate(self.fields):
            label[f] = QLabel(f)
            j+=1  

        I_entry = QLineEdit(frame)
        nplc_entry = QLineEdit(frame)
        I_button = QPushButton('Set Current')
        nplc_button = QPushButton('Set NPLC')
        I_button.clicked.connect(lambda: self.Set_I_K6221(I_entry))
        nplc_button.clicked.connect(lambda: self.set_NPLC(nplc_entry))
        layout = QGridLayout()
        
        for i, f in enumerate(self.fields):
            layout.addWidget(label[f], i, 0, 1, 1)
        layout.addWidget(I_entry, 0,1,1,1)
        layout.addWidget(nplc_entry, 1,1,1,1)
        layout.addWidget(I_button,0,2,1,1)
        layout.addWidget(nplc_button,1,2,1,1)
        layout.setRowStretch(j+1, 3)
        frame.setLayout(layout)
    
    def now_at(self, mode=0):
        return 0
    
    def stop_delta(self):
        self.instr.write('SOUR:SWE:ABOR')
    
    def sweep_val(self, val, pts,time):
        self.set_val(val)
    
    def set_val(self, val):
        self.instr.write('SOUR:DELT:HIGH {}'.format(val))
        self.current=val
    def src_i(self, val):
        self.instr.write('CLE')
        txt='SYST:COMM:SER:SEND ":SENS:VOLT:NPLC 5"'
        self.instr.write(txt)
        self.instr.write('CURR '+str(val))
        self.instr.write('CURR:COMP 10')
        self.instr.write('OUTP ON')
    def off_i(self):
        self.instr.write('OUTP OFF')
    def set_NPLC(self, entry):
        val = int(entry.text())
        txt='SYST:COMM:SER:SEND ":SENS:VOLT:NPLC '+str(val)+'"'
        self.instr.write(txt)
    
    def start_delta(self, val):        
        self.instr.write('*RST')
        self.instr.write('SOUR:DELT:HIGH {}'.format(val))
        # instr.write('SOUR:DELT:DEL 300e-3')
        self.instr.write('SOUR:DELT:ARM')
        self.instr.write('INIT:IMM')
    
    def start_didv(self, ilow, ihigh, istep, idelta, delay):
        pts=int(abs(ihigh-ilow)/istep)+1        
        self.instr.write('SYST:COMM:SER:SEND "VOLT:NPLC 20"')
        self.instr.write('*RST')
        self.instr.write('SOUR:DCON:STAR {}'.format(ilow))
        self.instr.write('SOUR:DCON:STOP {}'.format(ihigh))
        self.instr.write('SOUR:DCON:STEP {}'.format(istep))
        self.instr.write('SOUR:DCON:DELT {}'.format(idelta))
        self.instr.write('SOUR:DCON:DEL {}'.format(delay))
        self.instr.write('TRAC:POIN {}'.format(pts))
        # instr.write('SOUR:DELT:DEL 300e-3')
        self.instr.write('SOUR:DCON:ARM')
        self.instr.write('INIT:IMM')
    def finished(self):
        return self.instr.query('*OPC?')
    def get_data(self):
        dat=self.instr.query('TRAC:DATA?')
        dat=np.fromstring(dat, sep=',')
        dat=np.reshape(dat,(2,-1), order='F')
        return dat
    def Set_I_K6221(self, entry):
        val = float(entry.text())
        
        self.instr.write('*RST')
        self.instr.write('SOUR:DELT:HIGH {}'.format(val))
        # instr.write('SOUR:DELT:DEL 300e-3')
        self.instr.write('SOUR:DELT:ARM')
        self.instr.write('INIT:IMM')