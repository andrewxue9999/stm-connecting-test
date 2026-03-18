import os.path as osp
import numpy as np
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, 
                             QGridLayout, QGroupBox, QLabel, 
                             QLineEdit,QPushButton, QStyleFactory,  
                             QTabWidget, QTextEdit,QWidget, QFrame)

from PyQt5.QtTest import QTest
from PyQt5.QtGui import QPalette, QColor
from pyqtgraph.Qt import QtGui, QtCore
import sys
import pyqtgraph as pg
from Save1 import Savetxt
from Instruments_Bluefors import Instruments
import qcodes as qc

from GUI_functions2 import GUI_functions
import time

Instr = Instruments() #holds commands for all instruments connected to the computer
dic_lockin=[]
dic_instr=['None']
dic_loop = ['Inner loop', 'Middle loop','Outer loop']

#L_instr = len(dic_instr)
lists_tot = Instr.header() #List of all connected data channels
listX = ['Timestamp'] + ['B'] + ['T'] + ['Tv'] + dic_instr #List used for X axis to plot (maybe change this!!!)
listX.remove('None') 
GUI = GUI_functions(Instr.list_names)

class Main_Bluefors(QDialog):
    def __init__(self, parent=None):
        super (Main_Bluefors, self).__init__(parent)
        self.setGeometry(0,0,1000,500) #Set size of GUI
        pg.setConfigOptions(antialias=False)
        
        
        #Initialization of variables to build GUI
        self.save_data=[];self.instr_value=[]
        self.count = 0 #+1 everytime a point is taken
        self.count1 = 0;self.count2 = 0;self.count3 = 0 #+1 everytime a point in the corresponding loop is taken
        self.loop1 = 0;self.loop2 = 0;self.loop3 = 0 #+1 everytime the corresponding loop has run once
        
        self.sampleTime = 0
        self.StopIsClicked = False
        
        #Initialization of lists to save data
        self.full_data=np.array([[]])
        self.current_point=[]
        self.plotfrom=0
        self.tl=time.time()
        """
        Do we need these?
        """
        #Dictionaries for apearence
        
        self.check_value={}
        self.color_value={}
        self.symbol_value={}
        self.label_value={}
        self.edit_value={}
        
        self.in_loop={};self.in_loop_label={}
        self.mid_loop={};self.mid_loop_label={}
        self.out_loop={};self.out_loop_label={}
        self.B_loop={};self.B_loop_label={}
        self.T_loop={};self.T_loop_label={}
        
        #Apearence parameters
        self.originalPalette = QApplication.palette()
        
        self.font = QtGui.QFont()
        self.font.setFamily('Helvetica')
        self.font.setPointSize(16)
        self.font.setBold(True) 
        self.font.setItalic(True)
        
        #Is it better to have these functions return the widget and then place
        #the widget into the QGridLayout?
        self.createTopMostLeftGroup()
        self.createTopLeftGroupBox()
        self.createBottomLeftGroupBox()
        self.createTopMostMiddleGroup()
        self.createTopMiddleGroupBox()
        self.createTopRightGroupBox()
        self.createMiddleRightGroupBox()
        self.createBottomRightGroupBox()

        #Sets position of each group in the GUI
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.TopMostLeftGroup,0, 0, 1, 1)
        mainLayout.addWidget(self.TopLeftGroupBox, 1, 0, 1, 1)
        mainLayout.addWidget(self.BottomLeftGroupBox, 2, 0, 1, 1)
        mainLayout.addWidget(self.TopMostMiddleGroup,0, 1, 1, 2)
        mainLayout.addWidget(self.TopMiddleGroupBox, 1, 1, 3, 2)
        mainLayout.addWidget(self.TopRightGroupBox, 1, 3, 1, 1)
        mainLayout.addWidget(self.MiddleRightGroupBox, 2, 3, 1, 1)
        mainLayout.addWidget(self.BottomRightGroupBox, 3, 3, 1, 1)
        mainLayout.setColumnStretch(1,3)
        self.setLayout(mainLayout)

        self.setWindowTitle("DeanLab") #Title of the GUI window
        QApplication.setStyle(QStyleFactory.create('Fusion')) #Style of the GUI
        
    def createTopMostLeftGroup(self): #Save items
        self.TopMostLeftGroup = QGroupBox('SAVE')
        GUI.save_GUI(self.TopMostLeftGroup)
        
    def createTopLeftGroupBox(self): #Creates tab with all the lockins parameters
        self.TopLeftGroupBox = QGroupBox("LOCKIN")
        Tab_lockin = QTabWidget()
        for ins in Instr.lockins:
            tab = QWidget()
            Tab_lockin.addTab(tab,ins.name)
            ins.control_GUI(tab)
        
        layout = QGridLayout()
        layout.addWidget(Tab_lockin, 0, 0, 1, 1)
        
        for i in range(len(Instr.list_names)):
            if Instr.list_instr[i] == "DSP 7265":
                tabs = QTabWidget()

                display_frame = QWidget()
                Instr.instr[i].display_GUI(display_frame)
                tabs.addTab(display_frame, "Live Display")

                logger_frame = QWidget()
                Instr.instr[i].logger_GUI(logger_frame)
                tabs.addTab(logger_frame, "Data Logger")
                layout.addWidget(tabs, 1, 0, 1, 1)
        
        layout.setRowStretch(2, 1)
        self.TopLeftGroupBox.setLayout(layout)
        
    def createBottomLeftGroupBox(self): #Values of instruments updated live, chose which instrument to plot and color
        self.BottomLeftGroupBox = QFrame()
        
        for i, f in enumerate(lists_tot):
            self.check_value[i],self.color_value[i],self.symbol_value[i],self.label_value[i],self.edit_value[i] = GUI.ValueInstr_GUI(lists_tot[i])
            self.edit_value[i].setDisabled(True)
        l1 = QLabel('X to plot')
        self.Combo_l1 = QComboBox()
        x_list=['Time']+lists_tot
        self.Combo_l1.addItems(x_list)
        
        layout = QGridLayout()
        for i in range(len(lists_tot)):
            layout.addWidget(self.check_value[i], i, 0, 1, 1)
            layout.addWidget(self.label_value[i], i, 1, 1, 1)
            layout.addWidget(self.color_value[i], i, 2, 1, 1)
            layout.addWidget(self.symbol_value[i], i, 3, 1, 1)
            layout.addWidget(self.edit_value[i], i, 4, 1, 1)
        layout.addWidget(l1,len(lists_tot)+1,0,1,1)
        layout.addWidget(self.Combo_l1,len(lists_tot)+1,1,1,1)
        layout.setRowStretch(len(lists_tot)+1, 1)
        self.BottomLeftGroupBox.setLayout(layout)
        
    def createTopMostMiddleGroup(self): #Notes for saved file
        self.TopMostMiddleGroup = QGroupBox('NOTES')
        self.l1 = QTextEdit()
        layout = QGridLayout()
        layout.addWidget(self.l1,0,0,1,1)
        layout.setRowStretch(2,2)
        self.TopMostMiddleGroup.setLayout(layout)
        
    def createTopMiddleGroupBox(self): #Plot item
        self.TopMiddleGroupBox = QGroupBox("Plotting")
        Tab_plot = QTabWidget()
        livetab = QWidget()
        
        Tab_plot.addTab(livetab,'live plot')
        
        data=np.zeros((200,200))
        for i in range(200):
            for j in range(200):
                data[i,j]=np.sin(i*np.pi/100)*np.sin(j*np.pi/200) #Connect real data to this!
        
        self.TopMiddlePlot = pg.PlotWidget(parent=livetab)
        
        l1=QGridLayout()
        l1.addWidget(self.TopMiddlePlot, 0, 0, 1, 1)
        livetab.setLayout(l1)       
        
        layout = pg.GraphicsLayout()
        layout.addPlot()
        self.TopMiddlePlot.enableAutoRange('x','y', True)
        
        layout = QGridLayout()
        layout.addWidget(Tab_plot, 0, 0, 1, 1)
        layout.setRowStretch(1, 1)
        self.TopMiddleGroupBox.setLayout(l1)
    
        #Creating different plot for all the intruments to plot them on one figure at the time if needed
        self.ax1 = self.TopMiddlePlot.plot()
        self.ax2 = self.TopMiddlePlot.plot()
        self.ax3 = self.TopMiddlePlot.plot()
        self.ax4 = self.TopMiddlePlot.plot()
        self.ax5 = self.TopMiddlePlot.plot()
        self.ax6 = self.TopMiddlePlot.plot()
        self.ax7 = self.TopMiddlePlot.plot()
        self.ax8 = self.TopMiddlePlot.plot()
        self.ax9 = self.TopMiddlePlot.plot()
        self.ax10 = self.TopMiddlePlot.plot()
        self.ax11 = self.TopMiddlePlot.plot()
        self.ax12 = self.TopMiddlePlot.plot()
        self.ax13 = self.TopMiddlePlot.plot()
        self.ax14 = self.TopMiddlePlot.plot()
        self.ax15 = self.TopMiddlePlot.plot()
        self.plotData = {'x':[], 'y':[]}
        self.plotData1 = {'x':[], 'y':[]}
        self.plotData2 = {'x':[], 'y':[]}
        self.plotData3 = {'x':[], 'y':[]}
        self.plotData4 = {'x':[], 'y':[]}
        self.plotData5 = {'x':[], 'y':[]}
        self.plotData6 = {'x':[], 'y':[]}
        self.plotData7 = {'x':[], 'y':[]}
        self.plotData8 = {'x':[], 'y':[]} 
        self.plotData9 = {'x':[], 'y':[]}
        self.plotData10 = {'x':[], 'y':[]} 
        self.plotData11 = {'x':[], 'y':[]} 
        self.plotData12 = {'x':[], 'y':[]} 
        self.plotData13 = {'x':[], 'y':[]}
        self.plotData14 = {'x':[], 'y':[]}                                                                                                
        self.plotData15 = {'x':[], 'y':[]} 
        
    def createTopRightGroupBox(self): #to change parameters of instruments other than lockins. Tab created for every connected instrument (keithley and yoko)
        self.TopRightGroupBox= QGroupBox("INSTRUMENTS")
        Tab_instr = QTabWidget()
        for ins in Instr.not_lockins:
            tab = QWidget()
            Tab_instr.addTab(tab,ins.name)
            ins.control_GUI(tab)
        
        layout = QGridLayout()
        layout.addWidget(Tab_instr, 0, 0, 1, 1)
        
        """
        for i in range(len(Instr.list_names)):
            if Instr.list_instr[i] == "DSP 7265":
                Tab_display = QTabWidget()
                tab = QWidget()
                Tab_display.addTab(tab, "Parameters")
                Instr.instr[i].display_GUI(tab)
                layout.addWidget(Tab_display, 1, 0, 1, 1)
        """    
        
        
        layout.setRowStretch(1, 1)
        self.TopRightGroupBox.setLayout(layout)
        
    def createMiddleRightGroupBox(self): #control of sweeping parameters. Up to three loops. Separated if sweeping B or T
        self.MiddleRightGroupBox= QFrame()
        Tab_loop = QTabWidget()
        
        if 'Inner loop' in dic_loop:
            tab1 = QWidget()
            Tab_loop.addTab(tab1,"Inner loop")
            GUI.inLoop_GUI(self.in_loop_label, tab1)
        else:
            pass
        
        if 'Middle loop' in dic_loop:
            tab2 = QWidget()
            Tab_loop.addTab(tab2,"Outer loop")
            GUI.midLoop_GUI(self.mid_loop_label, tab2)
        else:
            pass
        
        # if 'Outer loop' in dic_loop:
        #     tab3 = QWidget()
        #     Tab_loop.addTab(tab3,"Outer loop")
        #     GUI.outLoop_GUI(self.out_loop_label, tab3)
        # else:
        #     pass
        
        review_button = QPushButton('Start loop')
        review_button.clicked.connect(lambda: GUI.loop_param()) #Button to set sweeping parameters
        
        layout = QGridLayout()
        layout.addWidget(Tab_loop, 0, 0, 1, 1)
        layout.addWidget(review_button, 1, 0, 1, 1)
        layout.setRowStretch(2, 1)
        self.MiddleRightGroupBox.setLayout(layout)
        
    def createBottomRightGroupBox(self):
        self.BottomRightGroupBox = QFrame()
        
        samplingLabel = QLabel('Sampling Time (s)')
        self.samplingEntry = QLineEdit()
        self.samplingEntry.setText('1')
        
        self.StartButton = QPushButton('START')
        self.StartButton.setStyleSheet("background-color: #142c76;")
       
        self.StartButton.clicked.connect(self.plotter)
        
        self.PauseButton = QPushButton('PAUSE')
        self.PauseButton.setStyleSheet("background-color: #8c6f18;" )
        
        self.PauseButton.clicked.connect(self.pauser)
        
        self.StopButton = QPushButton('STOP')
        self.StopButton.setStyleSheet("background-color: #76142c;" )
        self.StopButton.clicked.connect(self.stopper)
        
        self.clrButton = QPushButton('Clear graph')
        self.clrButton.clicked.connect(self.clr_plot)
        
        exitButton = QPushButton('CLOSE')
        exitButton.clicked.connect(self.QuitApp)
        
        layout = QGridLayout()
        layout.addWidget(samplingLabel, 0, 0, 1, 1)
        layout.addWidget(self.samplingEntry, 0, 1, 1, 1)
        layout.addWidget(self.PauseButton, 1, 0, 1, 1)
        layout.addWidget(self.StartButton, 1, 1, 1, 1)
        layout.addWidget(self.StopButton, 2, 1, 1, 1)
        layout.addWidget(self.clrButton, 2, 0, 1, 1)
        layout.addWidget(exitButton, 3, 0, 1, 2)
        layout.setRowStretch(3, 2)
        self.BottomRightGroupBox.setLayout(layout)
    
    def clr_plot(self): #Clears plot only, not the data
        self.plotfrom=self.count #mightm need -1
        
    def plotter(self): #Sets dim of measure and starts timer for live update. Creates folder and file to save
        numsave=len(lists_tot)
        if GUI.dim_meas == '1D':
            npts=GUI.step1*GUI.repeat1
        elif GUI.dim_meas == '2D':
            npts=GUI.step1*GUI.repeat1*GUI.step2*GUI.repeat2
        else:
            npts=1000
        
        self.full_data=np.zeros((npts,numsave))
        
        self.sampleTime = float(self.samplingEntry.text())
        self.savePlot = True if GUI.CheckSave.isChecked() == True else False
        self.done=False
        filename = GUI.filename_edit.text()
        folder = GUI.folder_edit.text()
        notes = self.l1.toPlainText()
        new_notes = notes.replace('\n','NEWLINE')
        with open('Record_folder.txt','wt') as f:
            f.write(f'name: {filename}\n')
            f.write(f'folder: {folder}\n')
            f.write(f'notes: {new_notes}\n')
        
        if self.savePlot == True:    
            if len(GUI.folder_edit.text()) == 0: #Default directory if not chosen
                path_name = 'C:/Users/thecd/Data'
                userdoc = osp.join(osp.expanduser("~"),path_name)
            else:
                userdoc = osp.join(osp.expanduser("~"),GUI.directory) #save file in chosen folder
            filename = GUI.filename_edit.text() #Use filename as entered in entry. If not filename the file will be saved with the date and hour of measurement
            header="\t".join(Instr.header())
               
            self.txt_mean = Savetxt(header,filename,userdoc,notes) #Creates file to save
            for i in range(len(Instr.list_names)):
                if Instr.list_instr[i] == "DSP 7265":
                    df=open(self.txt_mean.full_title,'w')
                    parameter_name = ["Frequency (Hz): ", "Voltage (V): ", "Time constant (s): ", "AC gain (dB): ", "Sensitivity (V): "]
                    parameter = Instr.instr[i].parameters
                    for i in range(len(parameter_name)):
                        df.write(parameter_name[i]+str(parameter[i])+"\n")
                    df.write("Sampling time (s): "+self.samplingEntry.text()+"\n")
                    df.close()
        else:
            pass
                    
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updater)
        self.timer.start(int(self.sampleTime*1000))
        
    def pauser(self):
        print('Pause')
        self.timer.stop()
        
    def stopper(self):
        self.StopIsClicked = True
        print('Stop')
        self.timer.stop()
        self.count = 0 #+1 everytime a point is taken
        self.count1 = 0;self.count2 = 0;self.count3 = 0; self.countB = 0; self.countT = 0 #+1 everytime a point in the corresponding loop is taken
        self.loop1 = 0;self.loop2 = 0;self.loop3 = 0; self.loopB = 0; self.loopT = 0; #+1 everytime the corresponding loop has run once
        self.sampleTime=0
        #Initialization of lists to save data
        self.plotfrom=0
        self.StopIsClicked = False
        
    def updater(self):#Function where plot, and saving of file happens
        
        if GUI.dim_meas == '1D':
            sweep_instr=Instr.get_instr(GUI.instr1)#Put this in start
            if self.count1 == 0 and self.loop1 == 0:
                #Sweep from initial value to starting point
                tostart=int(np.abs((GUI.start1-sweep_instr.now_at(0))/.1))+1
                sweep_instr.sweep_val(GUI.start1, tostart,.1)
                
            if self.count1 == GUI.step1: #Sweeps down instrument if sweep always in the same direction
                self.count1 = 0
                self.loop1+=1
                if GUI.dir1 == 'Same direction':
                    sweep_instr.sweep_val(GUI.start1, GUI.pointdown1,.1)
                    if self.loop1==GUI.repeat1:
                        self.stopper()
                        return                    
            else:
                sweep_instr.set_val(GUI.X1_plot[self.loop1][self.count1])

            QTest.qWait(int(GUI.wait1*1000))
            self.count1+= 1
           
        if GUI.dim_meas == '2D':
            sweep_instr1=Instr.get_instr(GUI.instr1)
            sweep_instr2=Instr.get_instr(GUI.instr2)
            if self.count1 == 0 and self.loop1 == 0: #Sweep to start
                sweep_instr1.sweep_val(GUI.start1,GUI.pointdown1,.1)
                sweep_instr2.sweep_val(GUI.start2,GUI.pointdown2,.1)

            if self.count1 == GUI.step1:#Move to next line
                self.count1 = 0
                self.loop1+=1
                if self.loop1 == GUI.repeat1: #Move to next line?
                    self.loop1 = 0
                    self.count2+=1
                    sweep_instr1.sweep_val(GUI.start1,GUI.pointdown1,.1)
                    if self.count2 == GUI.step2: #Map is finished
                        self.count2 = 0
                        self.loop2+=1
                        self.stopper()
                        sweep_instr2.sweep_val(GUI.start2,GUI.pointdown2,.1)
                        return
                    sweep_instr2.set_val(GUI.X2_plot[self.loop2][self.count2])
                    QTest.qWait(int(GUI.wait2*1000))

            #move forward normally
            sweep_instr2.set_val(GUI.X2_plot[self.loop2][self.count2])
            sweep_instr1.set_val(GUI.X1_plot[self.loop1][self.count1])
            QTest.qWait(int(GUI.wait1*1000)) 
            self.count1+=1
        
        if GUI.dim_meas=='None':
            #If not running a loop, this extends the limit of the data holder
            dat_limit=self.full_data[:,0].size
            if self.count==(dat_limit-1):
                newdat=np.zeros((dat_limit+1000,len(lists_tot)))
                newdat[:dat_limit]=self.full_data
                self.full_data=newdat
            #QTest.qWait(int(self.sampleTime*1000))
        
        self.current_point=Instr.measure()

        for ind, dat in enumerate(self.current_point):
            self.edit_value[ind].setText(str(dat))
        floatpoint=np.array([self.current_point])
        floatpoint=floatpoint.astype(float)
       
        self.full_data[self.count]=floatpoint
        
        if self.Combo_l1.currentIndex()==0:
            xdata=np.linspace(0,self.count,num=self.count)
        else:
            xdata=self.full_data[self.plotfrom:self.count,self.Combo_l1.currentIndex()-1]
        self.TopMiddlePlot.clear()
        
        for ind in range(len(self.current_point)):
            if self.check_value[ind].isChecked():
                pen = pg.mkPen(self.color_value[ind].color(mode='qcolor'))
                c = self.color_value[ind].color(mode='qcolor')
                sym = 'o' if self.symbol_value[ind].currentText()=='o' else None
                self.TopMiddlePlot.plot(xdata,self.full_data[self.plotfrom:self.count,ind],pen=pen, symbol=sym, symbolBrush=c)
      
        if self.savePlot == True:
            self.txt_mean.save_line(self.current_point)
        
        self.count+= 1

    def QuitApp(self):
        qc.Instrument.close_all()
        self.close()
            
#Lines to call the app and run it      
app = QApplication(sys.argv)
palette = QPalette()
palette.setColor(QPalette.Window, QColor(53, 53, 53))
palette.setColor(QPalette.WindowText, QtCore.Qt.white)
palette.setColor(QPalette.Base, QColor(25, 25, 25))
palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
palette.setColor(QPalette.ToolTipBase, QtCore.Qt.black)
palette.setColor(QPalette.ToolTipText, QtCore.Qt.white)
palette.setColor(QPalette.Text, QtCore.Qt.white)
palette.setColor(QPalette.Button, QColor(53, 53, 53))
palette.setColor(QPalette.ButtonText, QtCore.Qt.white)
palette.setColor(QPalette.BrightText, QtCore.Qt.red)
palette.setColor(QPalette.Link, QColor(42, 130, 218))
palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
palette.setColor(QPalette.HighlightedText, QtCore.Qt.black)
app.setPalette(palette)
gallery = Main_Bluefors()
gallery.show()
app.exec_()