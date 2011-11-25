# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Fri Nov 18 23:34:51 2011
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Tracks queue", None, QtGui.QApplication.UnicodeUTF8))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pages = QtGui.QStackedWidget(self.centralwidget)
        self.pages.setObjectName(_fromUtf8("pages"))
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.pages.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName(_fromUtf8("page_2"))
        self.pages.addWidget(self.page_2)
        self.horizontalLayout.addWidget(self.pages)
        MainWindow.setCentralWidget(self.centralwidget)
        self.lefttoolbar = QtGui.QToolBar(MainWindow)
        self.lefttoolbar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.lefttoolbar.setMovable(False)
        self.lefttoolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.lefttoolbar.setFloatable(False)
        self.lefttoolbar.setObjectName(_fromUtf8("lefttoolbar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.lefttoolbar)
        self.righttoolbar = QtGui.QToolBar(MainWindow)
        self.righttoolbar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar_2", None, QtGui.QApplication.UnicodeUTF8))
        self.righttoolbar.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.righttoolbar.setMovable(False)
        self.righttoolbar.setFloatable(False)
        self.righttoolbar.setObjectName(_fromUtf8("righttoolbar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.righttoolbar)
        self.actionHome = QtGui.QAction(MainWindow)
        self.actionHome.setCheckable(False)
        self.actionHome.setText(QtGui.QApplication.translate("MainWindow", "Home", None, QtGui.QApplication.UnicodeUTF8))
        self.actionHome.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+T", None, QtGui.QApplication.UnicodeUTF8))
        self.actionHome.setObjectName(_fromUtf8("actionHome"))
        self.actionProjects = QtGui.QAction(MainWindow)
        self.actionProjects.setText(QtGui.QApplication.translate("MainWindow", "Projects", None, QtGui.QApplication.UnicodeUTF8))
        self.actionProjects.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+P", None, QtGui.QApplication.UnicodeUTF8))
        self.actionProjects.setObjectName(_fromUtf8("actionProjects"))
        self.actionStarred = QtGui.QAction(MainWindow)
        self.actionStarred.setText(QtGui.QApplication.translate("MainWindow", "Starred", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStarred.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStarred.setObjectName(_fromUtf8("actionStarred"))
        self.actionCalendar = QtGui.QAction(MainWindow)
        self.actionCalendar.setText(QtGui.QApplication.translate("MainWindow", "Calendar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCalendar.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+L", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCalendar.setObjectName(_fromUtf8("actionCalendar"))
        self.actionTickler = QtGui.QAction(MainWindow)
        self.actionTickler.setText(QtGui.QApplication.translate("MainWindow", "Tickler", None, QtGui.QApplication.UnicodeUTF8))
        self.actionTickler.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+K", None, QtGui.QApplication.UnicodeUTF8))
        self.actionTickler.setObjectName(_fromUtf8("actionTickler"))
        self.actionAdmin = QtGui.QAction(MainWindow)
        self.actionAdmin.setText(QtGui.QApplication.translate("MainWindow", "Admin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdmin.setToolTip(QtGui.QApplication.translate("MainWindow", "Admin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdmin.setObjectName(_fromUtf8("actionAdmin"))
        self.actionView = QtGui.QAction(MainWindow)
        self.actionView.setText(QtGui.QApplication.translate("MainWindow", "View", None, QtGui.QApplication.UnicodeUTF8))
        self.actionView.setToolTip(QtGui.QApplication.translate("MainWindow", "view", None, QtGui.QApplication.UnicodeUTF8))
        self.actionView.setObjectName(_fromUtf8("actionView"))
        self.actionAdd = QtGui.QAction(MainWindow)
        self.actionAdd.setText(QtGui.QApplication.translate("MainWindow", "Add new", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+N", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd.setObjectName(_fromUtf8("actionAdd"))
        self.actionContexts = QtGui.QAction(MainWindow)
        self.actionContexts.setText(QtGui.QApplication.translate("MainWindow", "Contexts", None, QtGui.QApplication.UnicodeUTF8))
        self.actionContexts.setToolTip(QtGui.QApplication.translate("MainWindow", "Contexts", None, QtGui.QApplication.UnicodeUTF8))
        self.actionContexts.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
        self.actionContexts.setObjectName(_fromUtf8("actionContexts"))
        self.actionDone = QtGui.QAction(MainWindow)
        self.actionDone.setText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDone.setToolTip(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDone.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+D", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDone.setObjectName(_fromUtf8("actionDone"))
        self.lefttoolbar.addAction(self.actionHome)
        self.lefttoolbar.addAction(self.actionStarred)
        self.lefttoolbar.addAction(self.actionProjects)
        self.lefttoolbar.addAction(self.actionTickler)
        self.lefttoolbar.addSeparator()
        self.lefttoolbar.addAction(self.actionAdd)
        self.righttoolbar.addAction(self.actionAdmin)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        pass

