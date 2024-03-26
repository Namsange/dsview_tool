# from enum import Enum
# from PyQt5.QtGui import *

# from PyQt5.QtGui import QColor
# from PyQt5.QtGui import QFont
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore  # , QtGui
from mainUI import Ui_MainWindow

import win32api
import win32con
import win32gui


def getTime(dat):
    intTime = int(dat)
    seconds = intTime // 1000000000

    ns = intTime % 1000
    us = (intTime % 1000000) // 1000
    ms = intTime % 1000000000 // 1000000

    h = seconds // 3600
    m = seconds % 3600
    s = m % 60
    m = m // 60

    timStr = f'{h:02d}:{m:02d}:{s:02d}.{ms:03d}.{us:03d}.{ns:03d} '
    return timStr


def hexToAscii(data):
    asciiData = ''
    for i in data:
        dat = int(i, 16)
        if 0x20 <= dat <= 0x7e:
            asciiData += chr(dat)
        else:
            asciiData += '.'
    return asciiData


class myMainWindow(QMainWindow):
    def __init__(self):
        super(myMainWindow, self).__init__()
        self.mainui = None
        self.dwTxt = '.decCode_i2c'

    def setUI(self, ui: Ui_MainWindow):
        self.mainui = ui
        self.setWindowTitle('DSview 协议解析软件 V0.001')
        # self.mainui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.mainui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

    def dealWithFile(self, logFile, txtFile):
        startTime = 0
        startFlg = 0
        stopFlg = 0
        ackQut = 0
        RpStFlg = 0
        logData = ''

        logF = open(logFile, "r")
        txtF = open(txtFile, 'w+')

        lineList = logF.readlines()

        for line in lineList:
            line = line.strip()
            datList = line.split(',')
            # print(datList)

            if RpStFlg == 1:
                logData = 'Repeat_Start '
                RpStFlg = 0

            if ackQut == 1:
                if 'ACK' == datList[2]:
                    logData = logData + 'ACK '
                else:
                    logData = logData + 'NACK '
                ackQut = 0

            if 'Start' == datList[2]:
                if startFlg == 0:
                    startTime = float(datList[1])
                    startFlg = 1
                stopFlg = 0
                ackQut = 0
                logData = 'Start '

            if 'Start repeat' == datList[2]:
                ackQut = 0
                RpStFlg = 1
                stopTime = float(datList[1])
                i2cTime = stopTime - startTime
                stopFlg = 1

                srtTime = getTime(i2cTime)
                logData = srtTime + logData

            if 'Address write' in datList[2]:
                tog = datList[2].find('write: ') + 7
                i2cAddr = datList[2][tog:]
                logData = logData + i2cAddr + ' '

            if 'Address read' in datList[2]:
                tog = datList[2].find('read: ') + 6
                i2cAddr = datList[2][tog:]
                logData = logData + i2cAddr + ' '

            if 'Write' == datList[2]:
                i2cMode = 'Wr '
                ackQut = 1
                logData = logData + i2cMode

            if 'Read' == datList[2]:
                i2cMode = 'Rd '
                ackQut = 1
                logData = logData + i2cMode

            if 'Data write' in datList[2]:
                tog = datList[2].find('write: ') + 7
                i2cData = datList[2][tog:]
                logData = logData + i2cData + ' '
                ackQut = 1

            if 'Data read' in datList[2]:
                tog = datList[2].find('read: ') + 6
                i2cData = datList[2][tog:]
                logData = logData + i2cData + ' '
                ackQut = 1

            if 'Stop' in datList[2]:
                stopTime = float(datList[1])
                i2cTime = stopTime - startTime
                stopFlg = 1

                srtTime = getTime(i2cTime)
                logData = srtTime + logData

            if stopFlg == 1 or RpStFlg == 1:
                stopFlg = 0
                txtF.write(logData + '\r')
                # print(f'{logData}')

        txtF.close()

    def dealProcess(self):
        global color
        dfile = open(self.dwTxt, 'r')
        lineList = dfile.readlines()
        # rowPoint = self.mainui.tableWidget.rowCount()
        for line in lineList:
            # print(rowPoint)
            line = line.strip()
            datList = line.split(' ')
            if len(datList) > 4:
                rowPoint = self.mainui.tableWidget.rowCount()
                self.mainui.tableWidget.insertRow(rowPoint)
                self.mainui.tableWidget.setItem(rowPoint, 0, QtWidgets.QTableWidgetItem(datList[0]))
                self.mainui.tableWidget.item(rowPoint, 0).setTextAlignment(Qt.AlignCenter)
                self.mainui.tableWidget.setItem(rowPoint, 1, QtWidgets.QTableWidgetItem(datList[1]))
                self.mainui.tableWidget.setItem(rowPoint, 2,
                                                QtWidgets.QTableWidgetItem(hex(int(datList[2], 16) >> 1)[2:]))
                self.mainui.tableWidget.item(rowPoint, 2).setTextAlignment(Qt.AlignCenter)
                self.mainui.tableWidget.setItem(rowPoint, 3, QtWidgets.QTableWidgetItem(datList[3]))
                self.mainui.tableWidget.item(rowPoint, 3).setTextAlignment(Qt.AlignCenter)
                Err = 0
                colList = []
                data = []
                datCnt = 0
                for i in range(4, len(datList), 1):
                    if datList[i] == 'NACK':
                        Err = 1
                    elif datList[i] == 'ACK':
                        pass
                    else:
                        data.append(datList[i])

                    datCnt += 1
                    if datCnt >= 16 * 2:
                        colList.append(data)
                        datCnt = 0
                        data = []

                if len(data) != 0:
                    colList.append(data)

                rowOffset = 0
                for data in colList:
                    if rowOffset >= 1:  # 第二个 16byte
                        self.mainui.tableWidget.insertRow(rowPoint + rowOffset)
                        self.mainui.tableWidget.setItem(rowPoint + rowOffset, 0, QtWidgets.QTableWidgetItem(''))
                        self.mainui.tableWidget.setItem(rowPoint + rowOffset, 1, QtWidgets.QTableWidgetItem(''))
                        self.mainui.tableWidget.setItem(rowPoint + rowOffset, 2, QtWidgets.QTableWidgetItem(''))
                        self.mainui.tableWidget.setItem(rowPoint + rowOffset, 3, QtWidgets.QTableWidgetItem(''))
                        self.mainui.tableWidget.setItem(rowPoint + rowOffset, 5, QtWidgets.QTableWidgetItem(''))
                        self.mainui.tableWidget.setItem(rowPoint + rowOffset, 6, QtWidgets.QTableWidgetItem(''))
                    self.mainui.tableWidget.setItem(rowPoint + rowOffset, 4, QtWidgets.QTableWidgetItem(" ".join(data)))
                    self.mainui.tableWidget.setItem(rowPoint + rowOffset, 5, QtWidgets.QTableWidgetItem(hexToAscii(data)))
                    rowOffset += 1

                if Err == 1:
                    self.mainui.tableWidget.setItem(rowPoint, 6, QtWidgets.QTableWidgetItem('NACK'))
                else:
                    self.mainui.tableWidget.setItem(rowPoint, 6, QtWidgets.QTableWidgetItem(''))

                ''' 设置表格颜色 '''
                if datList[3] == 'Wr':
                    color = QColor(0xCC, 0xFF, 0xCC)
                elif datList[3] == 'Rd':
                    color = QColor(0xFF, 0xFF, 0x99)
                colPoint = self.mainui.tableWidget.columnCount()
                
                if rowOffset > 1:
                    for row in range(rowOffset):
                        for col in range(colPoint):
                            self.mainui.tableWidget.item(rowPoint + row, col).setBackground(QBrush(color))
                else:
                    for col in range(colPoint):
                        self.mainui.tableWidget.item(rowPoint, col).setBackground(QBrush(color))

        dfile.close()

    ''' 开始解析 按钮 '''
    def startResoveProtocol(self):
        self.clearContents()
        self.dealProcess()
        self.mainui.tableWidget.resizeColumnsToContents()

    ''' 打开文件 按钮 '''
    def openFile(self):
        fileName, filetype = QFileDialog.getOpenFileName(self,
                                                         "选取文件",
                                                         "./",
                                                         "All Files (*);;Text Files (*.txt)")
        self.dealWithFile(fileName, self.dwTxt)

    ''' 配置解析按钮 '''
    def configureProtocol(self):
        pass

    ''' 清空内容 '''
    def clearContents(self):
        while self.mainui.tableWidget.rowCount() > 0:
            self.mainui.tableWidget.removeRow(0)
