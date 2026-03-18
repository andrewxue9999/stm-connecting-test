import PyQt5
from PyQt5.QtWidgets import (QApplication,  QDialog, 
                             QGridLayout, QVBoxLayout,  QLabel, 
                             QPushButton, QStyleFactory,  
                             QFrame, QMessageBox)
from GUI_functions2 import GUI_functions
import sys
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMenu, QToolButton
from Instruments_Bluefors import Instruments
import pyvisa as visa
rm = visa.ResourceManager()
dic_instr=[]
GUI = GUI_functions(dic_instr)
list_instr = ['lockin1','lockin2','lockin3','lockin4','lockin5','lockin6','lockin7','lockin8','keithley1','keithley2','yoko','sim','rotator','dsp']
class Main_LoadInstr(QDialog):
    def __init__(self, parent=None):
        super (Main_LoadInstr, self).__init__(parent)
        self.setGeometry(50,50,100,500) #Set size of GUI
        
        #Apearence parameters
        self.originalPalette = QApplication.palette()
        
        self.font = QtGui.QFont()
        self.font.setFamily('Helvetica')
        self.font.setPointSize(16)
        self.font.setBold(True)
        self.font.setItalic(True)
        
        self.check_value={}
        self.color_value={}
        self.label_value={}
        self.edit_value={}
        self.instr_select={}
        self.ch_selector={}
        self.ch_menu={}
        self.dic={}
        self.list_instr=[]
        self.list_gpib_old=[]
        self.list_gpib_new=[]
        self.list_print=''
        self.my_instrument=[]
        self.itc3he_ch=['3He_high','3He_low','Sorb','1Kpot']
        self.sim_ch=['1','2','3','4','5','6','7','8']
        self.sr830_ch=['X','Y','R','Theta','AUX1','AUX2','AUX3','AUX4']
        self.sr860_ch=['X','Y','R','Theta']
        self.k2400_ch=['V','I']
        self.k2450_ch=['V','I']
        self.yoko_ch=['V','I']
        self.rotator_ch=['Theta','Phi']
        self.dsp_ch=['X','Y','R','Theta','DAC1','DAC2','DAC3','DAC4']
        self.test_ch=['Ch0','Ch1']
        self.ch_record=[]
        self.nspots=5
        self.createGroup()

        #Sets position of each group in the GUI
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.Group,0, 0, 1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("DeanLab - Load Instruments") #Title of the GUI window
        QApplication.setStyle(QStyleFactory.create('Fusion')) #Style of the GUI
 
    def createGroup(self):
        self.Group = QFrame()
        
        gpib_Label = QLabel('GPIB address')
        name_Label = QLabel('Instrument Name')
        
        for i in range(self.nspots):
            self.check_value[i],self.instr_select[i],self.label_value[i],self.edit_value[i] = GUI.LoadInstr_GUI()
            self.ch_selector[i]=QToolButton()
            self.ch_menu[i]=QMenu()
            self.ch_selector[i].setMenu(self.ch_menu[i])
            self.ch_selector[i].setPopupMode(QToolButton.InstantPopup)
            self.edit_value[i].setDisabled(True)
            self.instr_select[i].setDisabled(True)
            self.label_value[i].setDisabled(True)
            self.check_value[i].toggled.connect(self.instr_select[i].setEnabled)
            self.check_value[i].toggled.connect(self.edit_value[i].setEnabled)
            self.check_value[i].toggled.connect(self.edit_value[i].clear)
            self.check_value[i].toggled.connect(self.label_value[i].setEnabled)
            self.check_value[i].toggled.connect(self.label_value[i].clear)
            self.instr_select[i].currentIndexChanged.connect(lambda state, idx=i: self.changeMenu(self.instr_select[idx].currentText(), self.ch_menu[idx], idx))
            self.ch_record.append([])
        
        resourceButton = QPushButton('See available resources')
        resourceButton.clicked.connect(self.SeeInstr)
        
        testButton = QPushButton('Test Connections')
        testButton.clicked.connect(self.testConnect)
        
        exitButton = QPushButton('CLOSE')
        exitButton.clicked.connect(self.QuitApp)
        
        addButton = QPushButton('Add Instrument')
        addButton.clicked.connect(self.addrow)
        
        self.layout = QGridLayout()
        self.layout.addWidget(name_Label, 0, 2, 1, 1)
        self.layout.addWidget(gpib_Label, 0, 3, 1, 1)
        for i in range(self.nspots):
            self.layout.addWidget(self.check_value[i], i+1, 0, 1, 1)
            self.layout.addWidget(self.instr_select[i], i+1, 1, 1, 1)
            self.layout.addWidget(self.label_value[i], i+1, 2, 1, 1)
            self.layout.addWidget(self.edit_value[i], i+1, 3, 1, 1)
            self.layout.addWidget(self.ch_selector[i], i+1, 4, 1, 1)
        layout2 = QGridLayout()
        # layout2.addWidget(comment_Label,0,0,1,3)
        layout2.addWidget(resourceButton,2,0,1,1)
        layout2.addWidget(testButton,2,1,1,1)
        layout2.addWidget(addButton,2,2,1,1)
        layout2.addWidget(exitButton,2,3,1,1)
        
        # layout2.setRowStretch(len(list_instr)+1, 3)
        
        mainlayout = QVBoxLayout()
        mainlayout.addLayout(self.layout)
        mainlayout.addLayout(layout2)
        
        self.Group.setLayout(mainlayout)
        
    def changeMenu(self, instrument, menu, idx):
        menu.clear()
        self.ch_record[idx]=[]
        ind=0
        if instrument=='SR830':
            self.ch_record[idx]=[False, False, False, False, False, False, False, False]
            for i in self.sr830_ch:
                action = menu.addAction(i)
                action.setCheckable(True)
                action.triggered.connect(lambda state, x=idx, y=ind: self.addch(x,y))
                ind+=1
        elif instrument=='SR860':
            self.ch_record[idx]=[False, False, False, False]
            for i in self.sr860_ch:
                action = menu.addAction(i)
                action.setCheckable(True)
                action.triggered.connect(lambda state, x=idx, y=ind: self.addch(x,y))
                ind+=1
        elif instrument=='Keithley 2400':
            self.ch_record[idx]=[False, False]
            for i in self.k2400_ch:
                action = menu.addAction(i)
                action.setCheckable(True)
                action.triggered.connect(lambda state, x=idx, y=ind: self.addch(x,y))
                ind+=1
        elif instrument=='Keithley 2450':
            for i in self.k2450_ch:
                self.ch_record[idx]=[False, False]
                action = menu.addAction(i)
                action.setCheckable(True)
                action.triggered.connect(lambda state, x=idx, y=ind: self.addch(x,y))
                ind+=1
        elif instrument=='Yoko':
            for i in self.yoko_ch:
                self.ch_record[idx]=[False, False]
                action = menu.addAction(i)
                action.setCheckable(True)
                action.triggered.connect(lambda state, x=idx, y=ind: self.addch(x,y))
                ind+=1
        elif instrument=='Rotator':
            for i in self.rotator_ch:
                self.ch_record[idx]=[False, False]
                action = menu.addAction(i)
                action.setCheckable(True)
                action.triggered.connect(lambda state, x=idx, y=ind: self.addch(x,y))
                ind+=1
        elif instrument=='iTC 3He':
            for i in self.itc3he_ch:
                self.ch_record[idx]=[False, False, False, False]
                action = menu.addAction(i)
                action.setCheckable(True)
                action.triggered.connect(lambda state, x=idx, y=ind: self.addch(x,y))
                ind+=1
        elif instrument=='SIM':
            for i in self.sim_ch:
                self.ch_record[idx]=[False, False, False, False, False, False, False, False]
                action = menu.addAction(i)
                action.setCheckable(True)
                action.triggered.connect(lambda state, x=idx, y=ind: self.addch(x,y))
                ind+=1
        elif instrument=='DSP 7265':
            for i in self.dsp_ch:
                self.ch_record[idx]=[False, False, False, False, False, False, False, False]
                action = menu.addAction(i)
                action.setCheckable(True)
                action.triggered.connect(lambda state, x=idx, y=ind: self.addch(x,y))
                ind+=1
        elif instrument=='tester':
            for i in self.test_ch:
                self.ch_record[idx]=[False, False]
                action = menu.addAction(i)
                action.setCheckable(True)
                action.triggered.connect(lambda state, x=idx, y=ind: self.addch(x,y))
                ind+=1
    
    def addch(self, ins_id, ch_id):
        self.ch_record[ins_id][ch_id]=not self.ch_record[ins_id][ch_id]
        return
    
    def testConnect(self):
        
        self.write_file()        
        # self.list_gpib_old=[]
        # self.list_gpib_new=[]
        # self.read_file(self.list_gpib_old)
        # for i, f in enumerate(list_instr):
        #     if len(self.edit_value[i].text()) == 0:
        #         self.list_gpib_new.append('None')
        #     else:
        #         self.list_gpib_new.append(str(self.edit_value[i].text()))
        # for i in range(len(list_instr)):
        #     self.dic[self.list_instr[i]]=self.list_gpib_new[i]
        # self.write_file(self.list_gpib_old,self.list_gpib_new)
        
        ins=Instruments()
        print(ins.header())
    
    def addrow(self):
        i=self.nspots
        self.check_value[i],self.instr_select[i],self.label_value[i],self.edit_value[i] = GUI.LoadInstr_GUI()
        self.ch_selector[i]=QToolButton()
        self.ch_menu[i]=QMenu()
        self.ch_selector[i].setMenu(self.ch_menu[i])
        self.ch_selector[i].setPopupMode(QToolButton.InstantPopup)
        self.edit_value[i].setDisabled(True)
        self.check_value[i].toggled.connect(self.instr_select[i].setEnabled)
        self.check_value[i].toggled.connect(self.edit_value[i].setEnabled)
        self.check_value[i].toggled.connect(self.edit_value[i].clear)
        self.check_value[i].toggled.connect(self.label_value[i].setEnabled)
        self.check_value[i].toggled.connect(self.label_value[i].clear)
        self.instr_select[i].currentIndexChanged.connect(lambda state, idx=i: self.changeMenu(self.instr_select[idx].currentText(), self.ch_menu[idx], idx))
        self.ch_record.append([])
        self.layout.addWidget(self.check_value[i], i+1, 0, 1, 1)
        self.layout.addWidget(self.instr_select[i], i+1, 1, 1, 1)
        self.layout.addWidget(self.label_value[i], i+1, 2, 1, 1)
        self.layout.addWidget(self.edit_value[i], i+1, 3, 1, 1)
        self.layout.addWidget(self.ch_selector[i], i+1, 4, 1, 1)
        
        self.nspots+=1
    
    def write_file(self):
        #Open and clear file
        f = open('Instruments.txt', 'r+')
        f.truncate(0)
        for ind in range(self.nspots):
            if self.check_value[ind].isChecked():
                seq=[]
                seq.append('Name='+self.label_value[ind].text()+'\n')
                seq.append('Instrument='+self.instr_select[ind].currentText()+'\n')
                seq.append('GPIB='+self.edit_value[ind].text()+'\n')
                seq.append('channels='+str(self.ch_record[ind])+'\n')
                seq.append('\n')
                f.writelines(seq)
        f.close()
        # i=0
        # lines=[]
        # f = open('Instruments.txt', 'r+')
        # for line in f.readlines():
        #     if line.startswith('gpib')==True:
        #         lines.append(line.replace(listeOld[i],listeNew[i]+'\n'))
        #         i+=1
        #     else:
        #         lines.append(line)
        # f1 =  open('Instruments.txt', 'wt')
        # f1.writelines(lines)
        # f1.close()
                
    # def read_file(self,liste):
    #     with open('Instruments.txt', 'rt') as f:
    #         for line in f:
    #             if line.startswith('instrument')==True:
    #                 self.list_instr.append(line.split('=')[1])
    #             elif line.startswith('gpib')==True:
    #                 liste.append(line.split('=')[1])
    #             else:
    #                 pass
    #     for i in range(len(list_instr)):
    #         self.dic[self.list_instr[i]]=liste[i]
            
    def SeeInstr(self):
        rm = visa.ResourceManager()
        instrL=[]
        for i,f in enumerate(rm.list_resources()):
            if 'GPIB' in f:
                instr = rm.open_resource(f)
                try:
                    instr.query('*IDN?')
                    instrL.append(instr)
                except:
                    pass
        for i,f in enumerate(instrL):
            self.my_instrument.append(f)
            self.list_print+= str(f).split('::')[1]+'\t'
#            print(self.my_instrument[i].query('*IDN?').split(','))
            self.list_print+=str(self.my_instrument[i].query('*IDN?').split(',')[0])+' '+str(self.my_instrument[i].query('*IDN?').split(',')[1])+'\n'
        warning = QMessageBox()
        warning.setIcon(QMessageBox.Information)
        warning.setWindowTitle("Available resources")
        warning.setText(str(self.list_print))
        warning.setStandardButtons(QMessageBox.Ok)
        warning.exec()        
        
    def QuitApp(self):
        self.close()
    
#Lines to call the app and run it      
if __name__ == '__main__':
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
    gallery = Main_LoadInstr()
    gallery.show()
    sys.exit(app.exec_())