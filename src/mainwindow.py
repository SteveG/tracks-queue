#!/usr/bin/env python2.7
"""
    Copyright (C) 2010  Stephen Georg

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    For Questions about this program please contact
    Stephen Georg at srgeorg@gmail.com

    A copy of the license should be included in the file LICENSE.txt
"""

from PyQt4 import QtGui
from PyQt4 import QtCore
import logging
import sys
import sqlite3
import os
from ctypes import *
# Import the Designer file
from mainwindowui import Ui_MainWindow
# Import pages
from pagehome import PageHome
from pagestarred import PageStarred
from pageprojects import PageProjects
from pagetickler import PageTickler
from pagecalendar import PageCalendar
from pagedone import PageDone
from pageprojectview import PageProjectView
from pagecontexts import PageContexts
from pagecontextview import PageContextView
from pageadmin import PageAdmin

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        """Initiate the main window"""
        logging.info("Tracks initiated...")
        QtGui.QMainWindow.__init__(self)

        # for bling on windows(tm)
        self.doWinComposite = False
        try:
            if os.name == "nt" and self.isWindowsCompositionEnabled():
                    self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
                    from ctypes import windll, c_int, byref
                    windll.dwmapi.DwmExtendFrameIntoClientArea(c_int(self.winId()), byref(c_int(-1)))
                    self.doWinComposite = True
            QtCore.QDir.addSearchPath("image", sys.path[0] + "/")
        except:
            None
        
        # set the window icon
        self.setWindowIcon(QtGui.QIcon(sys.path[0] + "/icon.png"))
        
        # open the database file
        # Locate the database file, or create a new one
        knowFile = False
        self.settings = QtCore.QSettings("tracks-queue", "tracks-queue")
        # The last file accessed is contained in the settings
        if self.settings.contains("database/lastfile"):
            filepath = str(self.settings.value("database/lastfile").toString())
            if os.path.exists(filepath):
                #self.database = DbAccess(filepath)
                self.databaseCon = sqlite3.connect(filepath)
                self.databaseCon.row_factory = sqlite3.Row
                knowFile = True
        # If we have no record of the last file accessed
        if not knowFile:
            existing = QtGui.QMessageBox.question(self, "tracks queue: No file found", "Do you have an existing tracks database file?\n\n" +
            "No: \tA dialog will ask where to save a new database.\n" +
            "Yes: \tA dialog will ask where to find the existing database.\n", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            # User has an existing Database file
            if existing == QtGui.QMessageBox.Yes:
                dialog = QtGui.QFileDialog
                filename = dialog.getOpenFileName(self, "Open Database", QtCore.QDir.homePath(), "*.db")

                self.databaseCon = sqlite3.connect(str(filename))
                self.databaseCon.row_factory = sqlite3.Row
                self.settings.setValue("database/lastfile", QtCore.QVariant(filename))

            # User needs to create a  new Database file
            elif existing == QtGui.QMessageBox.No:
                dialog = QtGui.QFileDialog
                filename = dialog.getSaveFileName(self, "Save New Database", QtCore.QDir.homePath(), "*.db")
                templatePath = sys.path[0]
                templatePath = templatePath + "/template.db"

                # Copy the template database to the selected location
                import shutil
                shutil.copyfile(templatePath, filename)

                self.databaseCon = sqlite3.connect(str(filename))
                self.databaseCon.row_factory = sqlite3.Row
                self.settings.setValue("database/lastfile", QtCore.QVariant(filename))

        # Set up the user interface from Designer.
        self.setupUi(self)
        if self.doWinComposite:
            self.lefttoolbar.setStyleSheet("QToolBar { border: 0px }")
            self.righttoolbar.setStyleSheet("QToolBar { border: 0px }")
            self.setStyleSheet("QGroupBox { border: 0px }")
        
        # Restore window geometry
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry").toByteArray())
        
        # The pages, not created now apart from home
        self.pagehomeindex = None
        self.pagestarredindex = None
        self.pageprojectsindex = None
        self.pageprojectviewindex = None
        self.pageticklerindex = None
        self.pagecalendarindex = None
        self.pagedoneindex = None
        self.pagecontextsindex = None
        self.pagecontextviewindex = None
        self.pageadminindex = None
        
        self.pagehome = PageHome(self,self.databaseCon)
        self.pagehome.gotoProject.connect(self.slotGotoProject)
        self.pagehome.gotoContext.connect(self.slotGotoContext)
        #self.pagehome.refresh()
        #self.pages.insertWidget(0,self.pagehome)
        self.pagehomeindex = self.pages.addWidget(self.pagehome)
        self.pages.setCurrentIndex(self.pagehomeindex)
        
        # Get the current user
        if self.settings.contains("database/user"):
            self.current_user_id = int(self.settings.value("database/user").toString())
            self.pagehome.refresh(self.current_user_id)
        else:
            self.current_user_id = False
#            self.pageadmin.refresh()
#            self.pages.setCurrentIndex(9)
            self.pageadmin = PageAdmin(self, self.databaseCon)
            self.pageadmin.userChanged.connect(self.slotUserChanged)
            self.pageadmin.refresh()
            self.pageadminindex = self.pages.addWidget(self.pageadmin)
            self.pages.setCurrentIndex(self.pageadminindex)
        
        # Action Icons
        self.actionHome.setIcon(QtGui.QIcon(sys.path[0] + "/icons/home.png"))
        self.actionStarred.setIcon(QtGui.QIcon(sys.path[0] + "/icons/important.png"))
        self.actionProjects.setIcon(QtGui.QIcon(sys.path[0] + "/icons/projects.png"))
        self.actionTickler.setIcon(QtGui.QIcon(sys.path[0] + "/icons/tickler.png"))
        self.actionAdmin.setIcon(QtGui.QIcon(sys.path[0] + "/icons/admin.png"))
        self.actionAdd.setIcon(QtGui.QIcon(sys.path[0] + "/icons/add-new.png"))
        
        # Create Other actions
        # Repeating
        self.actionRepeating = QtGui.QAction(self)
        self.actionRepeating.setText(QtGui.QApplication.translate("MainWindow", "Repeating Actions", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRepeating.setObjectName(_fromUtf8("actionRepeating"))
        self.actionRepeating.setEnabled(False)
        # Statistics
        self.actionStatistics = QtGui.QAction(self)
        self.actionStatistics.setText(QtGui.QApplication.translate("MainWindow", "Statistics", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStatistics.setObjectName(_fromUtf8("actionStatistics"))
        self.actionStatistics.setEnabled(False)

        
        # Add the "View" toolbar menu
        self.viewMenu = QtGui.QMenu(self)
        self.viewMenu.addAction(self.actionCalendar)
        self.viewMenu.addAction(self.actionDone)
        self.viewMenu.addAction(self.actionStatistics)
        self.viewToolButton = QtGui.QToolButton(self)
        self.viewToolButton.setText("View")
        self.viewToolButton.setMenu(self.viewMenu)
        self.viewToolButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.righttoolbar.addWidget(self.viewToolButton)
        
        # Add the "Organise" toolbar menu
        self.organiseMenu = QtGui.QMenu(self)
        self.organiseMenu.addAction(self.actionContexts)
        self.organiseMenu.addAction(self.actionRepeating)
        self.organiseToolButton = QtGui.QToolButton(self)
        self.organiseToolButton.setText("Organise")
        self.organiseToolButton.setMenu(self.organiseMenu)
        self.organiseToolButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.righttoolbar.addWidget(self.organiseToolButton)      
        
        # Connect actions
        self.actionHome.triggered.connect(self.slotActionHome)
        self.actionStarred.triggered.connect(self.slotActionStarred)
        self.actionProjects.triggered.connect(self.slotActionProjects)
        self.actionTickler.triggered.connect(self.slotActionTickler)
        self.actionCalendar.triggered.connect(self.slotActionCalendar)
        self.actionContexts.triggered.connect(self.slotActionContexts)
        self.actionDone.triggered.connect(self.slotActionDone)
        self.actionAdmin.triggered.connect(self.slotActionAdmin)
        self.actionAdd.triggered.connect(self.slotActionAdd)
        
        
        
        # Set up keyboard shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("pgUp"),self,self.shortcutPageUp)
        QtGui.QShortcut(QtGui.QKeySequence("pgDown"),self,self.shortcutPageDown)
        QtGui.QShortcut(QtGui.QKeySequence("ctrl+pgDown"),self,self.shortcutCtrlPageDown)
        QtGui.QShortcut(QtGui.QKeySequence("ctrl+pgUp"),self,self.shortcutCtrlPageUp)

    def isWindowsCompositionEnabled(self):
        """Windows(tm) only method to detect whether composition is enabled"""
        value = c_long(False)
        point = pointer(value)
        windll.dwmapi.DwmIsCompositionEnabled(point)
        return bool(value.value)

    def paintEvent(self, e):
        """overridden method to include transparency for Windows if possible"""
        # This is a fix for the vista background transparency.
        if self.doWinComposite:
            p = QtGui.QPainter(self)
            p.setCompositionMode(QtGui.QPainter.CompositionMode_DestinationIn)
            p.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 0))

        QtGui.QMainWindow.paintEvent(self, e)

    def slotActionHome(self):
        logging.info("MainWindow->slotActionHome()")
        self.pagehome.refresh(self.current_user_id)
        self.pages.setCurrentIndex(self.pagehomeindex)
  
    def slotActionStarred(self):
        logging.info("MainWindow->slotActionStarred()")
        
        # create page if not already created
        if not self.pagestarredindex:
            self.pagestarred = PageStarred(self,self.databaseCon)
            self.pagestarred.gotoProject.connect(self.slotGotoProject)
            self.pagestarred.gotoContext.connect(self.slotGotoContext)
            self.pagestarredindex = self.pages.addWidget(self.pagestarred)
        
        self.pagestarred.refresh(self.current_user_id)
        self.pages.setCurrentIndex(self.pagestarredindex)
    
    def slotActionProjects(self):
        logging.info("MainWindow->slotActionProjects()")
        
        # create page if not already created
        if not self.pageprojectsindex:
            self.pageprojects = PageProjects(self, self.databaseCon)
            self.pageprojects.gotoProject.connect(self.slotGotoProject)
            self.pageprojectsindex = self.pages.addWidget(self.pageprojects)

        self.pageprojects.refresh(self.current_user_id)
        self.pages.setCurrentIndex(self.pageprojectsindex)

    def slotActionTickler(self):
        logging.info("MainWindow->slotActionTickler()")
        
        # create page if not already created
        if not self.pageticklerindex:
            self.pagetickler = PageTickler(self, self.databaseCon)
            self.pageticklerindex = self.pages.addWidget(self.pagetickler)

        self.pagetickler.refresh(self.current_user_id)
        self.pages.setCurrentIndex(self.pageticklerindex)

    def slotActionCalendar(self):
        logging.info("MainWindow->slotActionCalendar()")
        
        # create page if not already created
        if not self.pagecalendarindex:
            self.pagecalendar = PageCalendar(self, self.databaseCon)
            self.pagecalendar.gotoProject.connect(self.slotGotoProject)
            self.pagecalendar.gotoContext.connect(self.slotGotoContext)
            self.pagecalendarindex = self.pages.addWidget(self.pagecalendar)

        self.pagecalendar.refresh(self.current_user_id)
        self.pages.setCurrentIndex(self.pagecalendarindex)
        
    def slotActionContexts(self):
        logging.info("MainWindow->slotActionContexts()")
        
        # create page if not already created
        if not self.pagecontextsindex:
            self.pagecontexts = PageContexts(self, self.databaseCon)
            self.pagecontexts.gotoContext.connect(self.slotGotoContext)
            self.pagecontextsindex = self.pages.addWidget(self.pagecontexts)

        self.pagecontexts.refresh(self.current_user_id)
        self.pages.setCurrentIndex(self.pagecontextsindex)
        
    def slotActionDone(self):
        logging.info("MainWindow->slotActionDone()")
        
        # create page if not already created
        if not self.pagedoneindex:
            self.pagedone = PageDone(self, self.databaseCon)
            self.pagedone.gotoProject.connect(self.slotGotoProject)
            self.pagedone.gotoContext.connect(self.slotGotoContext)
            self.pagedoneindex = self.pages.addWidget(self.pagedone)

        self.pagedone.refresh(self.current_user_id)
        self.pages.setCurrentIndex(self.pagedoneindex)
        
    def slotActionAdmin(self):
        logging.info("MainWindow->slotActionAdmin()")
        
        # create page if not already created
        if not self.pageadminindex:
            self.pageadmin = PageAdmin(self, self.databaseCon)
            self.pageadmin.userChanged.connect(self.slotUserChanged)
            self.pageadminindex = self.pages.addWidget(self.pageadmin)
        
        self.pageadmin.refresh()
        self.pages.setCurrentIndex(self.pageadminindex)
    
    def slotActionAdd(self):
        logging.info("MainWindow->slotActionAdd()")
        index = self.pages.currentIndex()
        if index == self.pagehomeindex:
            self.pagehome.setFormVisible(True)
        elif index == self.pagestarredindex:
            self.pagestarred.setFormVisible(True)
        elif index == self.pageprojectsindex:
            self.pageprojects.setFormVisible(True)
        elif index == self.pageprojectviewindex:
            self.pageprojectview.setFormVisible(True)
        elif index == self.pageticklerindex:
            self.pagetickler.setFormVisible(True)
        elif index == self.pagecontextsindex:
            self.pagecontexts.setFormVisible(True)
        elif index == self.pagecontextviewindex:
            self.pagecontextview.setFormVisible(True)
        elif index == self.pagecalendarindex:
            self.pagecalendar.setFormVisible(True)
    
    def slotGotoProject(self, id):
        logging.info("MainWindow->slotGotoProject(self, id)")
        
        # create page if not already created
        if not self.pageprojectviewindex:
            self.pageprojectview = PageProjectView(self, self.databaseCon)
            self.pageprojectview.gotoProject.connect(self.slotGotoProject)
            self.pageprojectview.gotoContext.connect(self.slotGotoContext)
            self.pageprojectviewindex = self.pages.addWidget(self.pageprojectview)

        self.pageprojectview.setProject(id, self.current_user_id)
        self.pageprojectview.refresh(self.current_user_id)
        self.pages.setCurrentIndex(self.pageprojectviewindex)
    
    def slotGotoContext(self, id):
        logging.info("MainWindow->slotGotoContext(self, id)")
        
        # create page if not already created
        if not self.pagecontextviewindex:
            self.pagecontextview = PageContextView(self, self.databaseCon)
            self.pagecontextview.gotoProject.connect(self.slotGotoProject)
            self.pagecontextviewindex = self.pages.addWidget(self.pagecontextview)

        self.pagecontextview.setContext(id, self.current_user_id)
        self.pagecontextview.refresh(self.current_user_id)
        self.pages.setCurrentIndex(self.pagecontextviewindex)
        
    def slotUserChanged(self, userId):
        logging.info("MainWindow->slotUserChanged(self, "+str(userId)+")")
        self.current_user_id = userId
    
    def shortcutPageUp(self):
        logging.info("MainWindow->shortcutPageUp(self)")
        self.pagehome.moveExclusiveExpandUp()
    def shortcutPageDown(self):
        logging.info("MainWindow->shortcutPageDown(self)")
        self.pagehome.moveExclusiveExpandDown()
    def shortcutCtrlPageDown(self):
        logging.info("MainWindow->shortcutCtrlPageDown")
        self.pagehome.moveFocusDown()
    def shortcutCtrlPageUp(self):
        logging.info("MainWindow->shortcutCtrlPageUp")
        self.pagehome.moveFocusUp()

    
    
    def closeEvent(self, event):
        logging.info("MainWindow->closeEvent")
        self.settings.setValue("geometry", self.saveGeometry())



if __name__ == "__main__":
    # Start logging, first argument sets the level.

    LEVELS = {'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL}

    if len(sys.argv) > 1:
        level_name = sys.argv[1]
        level = LEVELS.get(level_name, logging.NOTSET)
        logging.basicConfig(level=level, format="%(asctime)s,%(msecs)03d %(message)s", datefmt='%H:%M:%S')

    #logging.debug('This is a debug message')
    #logging.info('This is an info message')
    #logging.warning('This is a warning message')
    #logging.error('This is an error message')
    #logging.critical('This is a critical error message')

    logging.info("tracks.pyqt initialising...")

    app = QtGui.QApplication(sys.argv)

    window = MainWindow()

    window.show()
    logging.info("tracks.pyqt executing...")
    app.exec_()
    logging.info("tracks.pyqt exiting...")
    sys.exit()
