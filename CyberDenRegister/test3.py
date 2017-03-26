from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sqlite3
import sys
import pandas as pd
class ABCTableModel(QtCore.QAbstractTableModel):
    def __init__(self,data,parent=None):
        QtCore.QAbstractTableModel.__init__(self,parent)
        self.__data=data     # Initial Data

    def rowCount( self, parent ):
        return len(self.__data)

    def columnCount( self , parent ):
        return len(self.__data)

    def data ( self , index , role ):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.__data[row][column]
            return QtCore.QString(str(value))

    def setData(self, index, value):
        self.__data[index.row()][index.column()] = value
        return True

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsSelectable      

    def insertRows(self , position , rows , item , parent=QtCore.QModelIndex()):
        # beginInsertRows (self, QModelIndex parent, int first, int last)
        self.beginInsertRows(QtCore.QModelIndex(),len(self.__data),len(self.__data)+1)
        self.__data.append(item) # Item must be an array
        self.endInsertRows()
        return True

class Ui_MainWindow(QtGui.QMainWindow , QtGui.QWidget):
    def __init__(self):
        QtGui.QMainWindow.__init__(self,None)
        QtGui.QWidget.__init__(self,None)

    def setupUi(self, MainWindow):
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableView = QtGui.QTableView(self.centralwidget)
        self.tableModel=ABCTableModel([[1,2,3],[2,3,4],[4,5,6]])
        self.tableView.setModel(self.tableModel) 
        self.lineEdit_1 = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit_2 = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit_3 = QtGui.QLineEdit(self.centralwidget)
        self.tableModel.insertRows(self.lineEdit_1.text(),self.lineEdit_2.text(), self.lineEdit_3.text())

if  __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow() # <-- Instantiate QMainWindow object.
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())