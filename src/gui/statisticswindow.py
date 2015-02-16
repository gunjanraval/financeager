#!/usr/bin/python

""" Defines the StatisticsWindow Popup for the Financeager application. """

# define authorship information
__authors__     = ['Philipp Metzner']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2014'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Philipp Metzner'
__email__       = 'beth.aleph@yahoo.de'


from PyQt4 import QtGui, QtCore 
from items import ExpenseItem 
from . import loadUi, _MONTHS_ 

class StatisticsWindow(QtGui.QDialog):
    """
    StatisticsWindow class for the Financeager application.
    This window can be opened by either clicking the corresponding button in
    the toolbar or typing the shortcut CTRL-t. 
    It displays a table with receipts, expenditures and their difference for
    all twelve months. 
    The widget basically is a QTreeView that is populated with a
    QStandardItemModel created from the FinanceagerWindow's items.
    
    :attribute      self.__totals | list 
                    Keeps track of total expenditures and receipts, resp.
                    Updated via updateTotalItems() upon item change. 
    """

    def __init__(self, parent=None):
        """
        Loads the ui layout file. 
        Populates the model and does some layout adjustments. 
        
        :param      parent | FinanceagerWindow 
        """
        super(StatisticsWindow, self).__init__(parent)
        loadUi(__file__, self)

        self.__model = QtGui.QStandardItemModel(self.tableView)
        self.__model.setHorizontalHeaderLabels(
                ['Expenditures', 'Receipts', 'Differences'])
        self.__model.setVerticalHeaderLabels(_MONTHS_ + ['TOTAL'])
        monthsTabWidget = self.parentWidget().monthsTabWidget
        for r in range(12):
            self.__model.setItem(r, 0, monthsTabWidget.widget(r).expendituresModel().valueItem())
            self.__model.setItem(r, 1, monthsTabWidget.widget(r).receiptsModel().valueItem())
            self.__model.setItem(r, 2, ExpenseItem('0'))
        for c in range(3):
            self.__model.setItem(12, c, ExpenseItem('0'))
        self.__totals = [0, 0]
        #FIXME does not update February etc
        self.updateTotalItems(self.__model.item(0, 0))
        self.updateTotalItems(self.__model.item(0, 1))
        self.tableView.setModel(self.__model)

        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableView.adjustSize()
        self.setWindowTitle('Statistics of ' + str(parent.year()))
        self.setFixedSize(self.size())
        # CONNECTIONS
        self.__model.itemChanged.connect(self.updateTotalItems)

    def closeEvent(self, event):
        """ Reimplementation. Unchecks the action_Statistics of the MainWindow. """
        self.parentWidget().action_Statistics.setChecked(False)
        event.accept()

    def keyPressEvent(self, event):
        """ Reimplementation. Unchecks the action_Statistics of the MainWindow. """
        if event.key() == QtCore.Qt.Key_Escape:
            self.parentWidget().action_Statistics.setChecked(False)
        super(StatisticsWindow, self).keyPressEvent(event)

    def updateTotalItems(self, item):
        """
        Whenever an item in the table is changed, one of the 'total' items 
        needs to be updated, i.e. the sum of all month values is calculated.
        Also, the corresponding value in third column (difference) is updated.
        This function is ignored if an item in the third column is changed
        (this will happen because Item.setValue() emits itemChanged() signal).

        :param      item | Item emitted from itemChanged() signal
        """
        if item.column() == 2:
            return 
        total = 0.0
        c = int(item.column())
        for r in range(12):
            total += self.__model.item(r, c).value()
            if r == item.row():
                self.__model.item(r, 2).setValue(
                        self.__model.item(r, 1).value() - 
                        self.__model.item(r, 0).value())
        self.__model.item(12, c).setValue(total)
        self.__totals[c] = total 
        difference = self.__totals[1] - self.__totals[0]
        self.__model.item(12, 2).setValue(difference)
