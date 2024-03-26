import os
import sys

from PyQt5 import QtCore, QtGui
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QApplication

sys.path.append(os.getcwd())

from mainUI import Ui_MainWindow
from myMainWindow import myMainWindow

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtGui.QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    a = QApplication(sys.argv)
    MainWindow = myMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    # ico_path = os.path.join(os.path.dirname(__file__), './ico/logo.ico')
    # icon = QtGui.QIcon()
    # icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    # MainWindow.setWindowIcon(icon)
    MainWindow.setUI(ui)
    MainWindow.show()
    sys.exit(a.exec_())
