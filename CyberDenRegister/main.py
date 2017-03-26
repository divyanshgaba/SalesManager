#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore, QtSql
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sqlite3
import sys
import pandas as pd


class MyDB:
    db_connection = None
    db_cur = None
    def __init__(self):
        self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.db.setHostName("localhost")
        self.db.setDatabaseName("database/main.db")
        self.db.setUserName("root")
        self.db.setPassword("")
        ok = self.db.open()
        if not ok:
            QtGui.QMessageBox.warning(self, "Error", "Invalid database!")
            return
        self.create_table()
    def create_table(self):
        self.db.exec_("\
                CREATE TABLE IF NOT EXISTS  payment ('id'  INTEGER PRIMARY KEY AUTOINCREMENT ,\
                'Amount'  INT(10)    NOT NULL ,  'Alt Number'  INT(15)    NULL DEFAULT NULL ,\
                'Party Name'  VARCHAR(50)  ,'Particular' INT(10),  'Date Time'  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        self.db.exec_("\
                CREATE TABLE IF NOT EXISTS  sale ('id'  INTEGER PRIMARY KEY AUTOINCREMENT ,\
                'Company'  VARCHAR(50) NOT NULL ,  'Phone Number'  INT(15)    NOT NULL ,\
                'Amount'  NUMBER(10)    NOT NULL ,  'Alt Number'  INT(15)    NULL DEFAULT NULL ,\
                'Party Name'  VARCHAR(50) NULL , 'Company Name' VARCHAR(50), 'Company Balance' NUMBER,\
                'Date Time'  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , 'Type' CHAR(10) NOT NULL,\
                'Status'  TINYINT(2) NOT NULL )")
    def insert_cash_sale(self,values):
        query = QtSql.QSqlQuery(self.db)
        query.prepare("INSERT INTO sale('Company','Phone Number','Amount','Alt Number','Type','Status')\
                            VALUES(?, ?, ?, ?, ?, ?)")
        query.addBindValue(values)
        query.exec_()
        #self.db.exec_("INSERT INTO sale('Company','Phone Number','Amount','Alt Number','Type','Status')\
                   #         VALUES(?, ?, ?, ?, ?, ?)", values)

    def insert_credit_sale(self,values):
        self.db.exec_("INSERT INTO sale('Company','Phone Number','Amount','Alt Number','Party Name','Type','Status')\
                            VALUES(?, ?, ?, ?, ?, ?, ?)", values)

    def insert_cash_in_payment(self,values):
        self.db.exec_("INSERT INTO payment('Party Name', 'Alt Number', 'Amount') VALUES(?, ?, ?)", values)

    def insert_cash_out_payment(self,values):
        self.db.exec_("INSERT INTO payment('Party Name', 'Amount', 'Particular') VALUES(?, ?, ?)", values)

    def pending_data(self):
        sql = "SELECT * from sale where status = 1"
        df = pd.read_sql(sql, self.db)
        df.index.name = "S.No"
        del df["Status"], df["id"]
        print(df)
        return df
    def __del__(self):
        self.db.close()


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data


    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
                return str(
                    self._data.iloc[index.row(),index.column()])
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            try:
                return '%s' % self._data.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                return '%s' % self._data.index.tolist()[section]
            except (IndexError, ):
                return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            self._data.iloc[index.row(),index.column()] = value.toByteArray().data()
            if self.data(index,QtCore.Qt.DisplayRole) == value.toByteArray().data():
                self.dataChanged.emit(index, index)
                return True
        return False


class App(QtGui.QWidget):

    def __init__(self):
        super(App, self).__init__()
        self.db = MyDB()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1200, 800)
        self.setWindowTitle('Register')
        self.setWindowIcon(QtGui.QIcon('web.png'))
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)
        self.add_gridsale()
        self.add_gridpayment()
        self.add_gridpending()
        self.add_gridreport()
        self.setLayout(self.grid)
        self.show()

    def add_gridsale(self):

        gridsale = QtGui.QGridLayout()
        cashsale_btn = QtGui.QPushButton("Cash Sale")
        cashsale_btn.clicked.connect(self.cash_sale_dialog)
        cashsale_btn.resize(cashsale_btn.sizeHint())
        gridsale.addWidget(cashsale_btn, 1, 0)

        creditsale_btn = QtGui.QPushButton("Credit Sale")
        creditsale_btn.resize(creditsale_btn.sizeHint())
        creditsale_btn.clicked.connect(self.credit_sale_dialog)
        gridsale.addWidget(creditsale_btn, 1, 1)
        self.grid.addLayout(gridsale, 0, 0, 3, 1)

    def add_gridpayment(self):
        gridpayment = QtGui.QGridLayout()
        cashin_btn = QtGui.QPushButton("Cash In")
        cashin_btn.resize(cashin_btn.sizeHint())
        gridpayment.addWidget(cashin_btn, 1, 0)
        cashin_btn.clicked.connect(self.show_cash_in_dialog)

        cashout_btn = QtGui.QPushButton("Cash Out")
        cashout_btn.resize(cashout_btn.sizeHint())
        gridpayment.addWidget(cashout_btn, 1, 1)
        cashout_btn.clicked.connect(self.show_cash_out_dialog)
        self.grid.addLayout(gridpayment, 0, 1, 3, 1)

    def add_gridpending(self):
        gridpending = QtGui.QGridLayout()

        self.db_table = QtGui.QTableView(self)
        self.model = QtSql.QSqlQueryModel()
        self.model.setQuery("SELECT * FROM sale")
        self.db_table.setModel(self.model)
        #self.db_table.hideColumn(0)  # hide column 'id'
        self.db_table.hideColumn(6)  #
        self.db_table.hideColumn(7)  #
        self.db_table.hideColumn(9)
        self.db_table.hideColumn(10)  # hide column 'status'
        #self.db_table.
        self.db_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)  # select Row
        self.db_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)  # disable multiselect
        self.db_table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        gridpending.addWidget(self.db_table, 0, 0, 1, 5)

        done_btn = QtGui.QPushButton("Done")
        done_btn.resize(done_btn.sizeHint())
        gridpending.addWidget(done_btn, 1, 4)
        #done_btn.clicked.connect(self.submit_from_pending)

        cancel_btn = QtGui.QPushButton("Cancel")
        cancel_btn.resize(cancel_btn.sizeHint())
        gridpending.addWidget(cancel_btn, 1, 3)
        cancel_btn.clicked.connect(self.cancel_from_pending)

        self.grid.addLayout(gridpending, 4, 0, 8, 2)

        '''     self.view = QtGui.QTableView()
        self.model = PandasModel(self.db.pending_data())
        self.view.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.view.setModel(self.model)
        gridpending.addWidget(self.view)
        self.grid.addLayout(gridpending, 4, 0, 8, 2)
        '''




    def add_gridreport(self):

        gridreport = QtGui.QGridLayout()
        test2 = QtGui.QLabel("test2")
        test2.resize(test2.sizeHint())
        test2.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        test2.setStyleSheet('background: green')
        gridreport.addWidget(test2, 0, 0, 1, 1)
        self.grid.addLayout(gridreport, 12, 0, 8, 2)

    def cash_sale_dialog(self):

        self.cash_dialog = QDialog()
        self.cash_dialog.setWindowTitle("Cash Sale")
        dialog_grid = QtGui.QGridLayout()
        dialog_grid.setSpacing(10)

        buttongrid = QtGui.QGridLayout()

        cancel_button = QtGui.QPushButton("Cancel")
        cancel_button.resize(cancel_button.sizeHint())
        cancel_button.clicked.connect(self.cash_dialog.close)
        cancel_button.setFont(QtGui.QFont('Times', 12))
        buttongrid.addWidget(cancel_button, 0, 0)

        submit_button = QtGui.QPushButton("Submit")
        submit_button.resize(submit_button.sizeHint())
        submit_button.clicked.connect(self.cash_submit)
        submit_button.setFont(QtGui.QFont('Times', 12))
        buttongrid.addWidget(submit_button, 0, 1)

        label_field_name = ["Company Name", "Phone Number", "Amount", "Alt Number"]

        self.text_field = []
        self.label_field = []
        for name in label_field_name:
            self.text_field.append(QtGui.QLineEdit())
            self.label_field.append(QtGui.QLabel(name))

        for i, label, LineEdit in zip(range(len(self.label_field)), self.label_field,
                                      self.text_field):
            label.setFont(QtGui.QFont('Times', 16))
            LineEdit.setFont(QtGui.QFont('Times', 16))
            #           LineEdit.setPlaceholderText(label.text())
            LineEdit.resize(LineEdit.sizeHint())
            dialog_grid.addWidget(label, i, 0)
            dialog_grid.addWidget(LineEdit, i, 1)
        dialog_grid.addLayout(buttongrid, i + 1, 1)

        self.cash_dialog.setWindowModality(Qt.ApplicationModal)
        self.cash_dialog.setLayout(dialog_grid)
        self.cash_dialog.exec_()

    def cash_submit(self):
        values = []
        for label, LineEdit in zip(self.label_field, self.text_field):
            values.append(LineEdit.text())
        values.extend(["Cash", 1])
        values = tuple(values)
        print(values)
        self.db.insert_cash_sale(values)
        print("Success")
        #self.view.update()
        self.cash_dialog.close()

    def credit_sale_dialog(self):
        self.credit_dialog = QDialog()
        self.credit_dialog.setWindowTitle("Credit Sale")
        dialog_grid = QtGui.QGridLayout()
        dialog_grid.setSpacing(10)

        buttongrid = QtGui.QGridLayout()

        cancel_button = QtGui.QPushButton("Cancel")
        cancel_button.resize(cancel_button.sizeHint())
        cancel_button.clicked.connect(self.credit_dialog.close)
        cancel_button.setFont(QtGui.QFont('Times', 12))
        buttongrid.addWidget(cancel_button, 0, 0)

        submit_button = QtGui.QPushButton("Submit")
        submit_button.resize(submit_button.sizeHint())
        submit_button.clicked.connect(self.credit_submit)
        submit_button.setFont(QtGui.QFont('Times', 12))
        buttongrid.addWidget(submit_button, 0, 1)
        label_field_name = ["Company Name", "Phone Number", "Amount", "Alt Number", "Party Name"]

        self.text_field = []
        self.label_field = []
        for name in label_field_name:
            self.text_field.append(QtGui.QLineEdit())
            self.label_field.append(QtGui.QLabel(name))

        for i, label, LineEdit in zip(range(len(self.label_field)), self.label_field,
                                      self.text_field):
            label.setFont(QtGui.QFont('Times', 16))
            LineEdit.setFont(QtGui.QFont('Times', 16))
            #           LineEdit.setPlaceholderText(label.text())
            LineEdit.resize(LineEdit.sizeHint())
            dialog_grid.addWidget(label, i, 0)
            dialog_grid.addWidget(LineEdit, i, 1)
        dialog_grid.addLayout(buttongrid, i + 1, 1)

        self.credit_dialog.setWindowModality(Qt.ApplicationModal)
        self.credit_dialog.setLayout(dialog_grid)
        self.credit_dialog.exec_()

    def credit_submit(self):
        values = []
        for label, LineEdit in zip(self.label_field, self.text_field):
            if LineEdit.text() == "" and label.text() != "Alt Number":
                return
            else:
                values.append(LineEdit.text())
        values.extend(["Credit", 1])
        values = tuple(values)
        self.db.insert_credit_sale(values)
        print("Success")
        self.credit_dialog.close()

    def show_cash_in_dialog(self):
        self.cash_in_dialog = QDialog()
        self.cash_in_dialog.setWindowTitle("Cash In")
        dialog_grid = QtGui.QGridLayout()
        dialog_grid.setSpacing(10)

        buttongrid = QtGui.QGridLayout()

        cancel_button = QtGui.QPushButton("Cancel")
        cancel_button.resize(cancel_button.sizeHint())
        cancel_button.clicked.connect(self.cash_in_dialog.close)
        cancel_button.setFont(QtGui.QFont('Times', 12))
        buttongrid.addWidget(cancel_button, 0, 0)

        submit_button = QtGui.QPushButton("Submit")
        submit_button.resize(submit_button.sizeHint())
        submit_button.clicked.connect(self.cash_in_submit)
        submit_button.setFont(QtGui.QFont('Times', 12))
        buttongrid.addWidget(submit_button, 0, 1)
        label_field_name = ["Party Name", "Alt Number", " Amount"]

        self.text_field = []
        self.label_field = []
        for name in label_field_name:
            self.text_field.append(QtGui.QLineEdit())
            self.label_field.append(QtGui.QLabel(name))

        for i, label, LineEdit in zip(range(len(self.label_field)), self.label_field,
                                      self.text_field):
            label.setFont(QtGui.QFont('Times', 16))
            LineEdit.setFont(QtGui.QFont('Times', 16))
            #           LineEdit.setPlaceholderText(label.text())
            LineEdit.resize(LineEdit.sizeHint())
            dialog_grid.addWidget(label, i, 0)
            dialog_grid.addWidget(LineEdit, i, 1)
        dialog_grid.addLayout(buttongrid, i + 1, 1)

        self.cash_in_dialog.setWindowModality(Qt.ApplicationModal)
        self.cash_in_dialog.setLayout(dialog_grid)
        self.cash_in_dialog.exec_()

    def cash_in_submit(self):
        values = []
        for label, LineEdit in zip(self.label_field, self.text_field):
            if LineEdit.text() == "" and label.text() != "Alt Number":
                return
            else:
                values.append(LineEdit.text())
        values = tuple(values)
        self.db.insert_cash_in_payment(values)
        print("Success")
        self.cash_in_dialog.close()

    def show_cash_out_dialog(self):
        self.cash_out_dialog = QDialog()
        self.cash_out_dialog.setWindowTitle("Cash Out")
        dialog_grid = QtGui.QGridLayout()
        dialog_grid.setSpacing(10)

        buttongrid = QtGui.QGridLayout()

        cancel_button = QtGui.QPushButton("Cancel")
        cancel_button.resize(cancel_button.sizeHint())
        cancel_button.clicked.connect(self.cash_out_dialog.close)
        cancel_button.setFont(QtGui.QFont('Times', 12))
        buttongrid.addWidget(cancel_button, 0, 0)

        submit_button = QtGui.QPushButton("Submit")
        submit_button.resize(submit_button.sizeHint())
        submit_button.clicked.connect(self.cash_out_submit)
        submit_button.setFont(QtGui.QFont('Times', 12))
        buttongrid.addWidget(submit_button, 0, 1)
        label_field_name = ["Party Name", "Amount", "Particular"]

        self.text_field = []
        self.label_field = []
        for name in label_field_name:
            self.text_field.append(QtGui.QLineEdit())
            self.label_field.append(QtGui.QLabel(name))

        for i, label, LineEdit in zip(range(len(self.label_field)), self.label_field,
                                      self.text_field):
            label.setFont(QtGui.QFont('Times', 16))
            LineEdit.setFont(QtGui.QFont('Times', 16))
            #           LineEdit.setPlaceholderText(label.text())
            LineEdit.resize(LineEdit.sizeHint())
            dialog_grid.addWidget(label, i, 0)
            dialog_grid.addWidget(LineEdit, i, 1)
        dialog_grid.addLayout(buttongrid, i + 1, 1)

        self.cash_out_dialog.setWindowModality(Qt.ApplicationModal)
        self.cash_out_dialog.setLayout(dialog_grid)
        self.cash_out_dialog.exec_()

    def cash_out_submit(self):
        values = []
        for label, LineEdit in zip(self.label_field, self.text_field):
            if LineEdit.text() == "":
                return
            else:
                values.append(LineEdit.text())
        values = tuple(values)
        self.db.insert_cash_out_payment(values)
        print("Success")
        self.cash_out_dialog.close()

    def cancel_from_pending(self):
        cancel_msg = "Are you sure you want to Cancel this order?"
        reply = QtGui.QMessageBox.question(self, 'Message', cancel_msg, QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            pass

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ob = App()
    sys.exit(app.exec_())
