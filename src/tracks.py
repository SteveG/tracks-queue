#!/usr/bin/env python
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
import sys
import sqlite3
import os
from ctypes import *
# Import the Designer file
from tracksui import Ui_MainWindow
# Import tracks widgets
from tracksActionList import TracksActionList
from tracksActionEditor import TracksActionEditor
from tracksProjectWidgets import TracksProjectList, TracksProjectEditor
from tracksContextWidgets import TracksContextList, TracksContextEditor


class Tracks(QtGui.QMainWindow, Ui_MainWindow):
    """Tracks is the main window class for tracks.cute"""
    
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
            QtCore.QDir.addSearchPath("image", sys.path[0]+"/")
        except:
            None

        
        
        
        
        
        self.setWindowIcon(QtGui.QIcon(sys.path[0] + "/icon.png"))
        # open the database file
        # Locate the database file, or create a new one
        knowFile = False
        self.settings = QtCore.QSettings("tracks.cute", "tracks.cute")
        # The last file accessed is contained in the settings
        if self.settings.contains("database/lastfile"):
            filepath = str(self.settings.value("database/lastfile").toString())
            if os.path.exists(filepath):
                #self.database = DbAccess(filepath)
                self.databaseCon = sqlite3.connect(filepath)
                self.databaseCon.row_factory = sqlite3.Row
                knowFile = True
        # We have no record of the last file accessed
        if not knowFile:
            existing = QtGui.QMessageBox.question(self, "tracks.cute: No file found", "Do you have an existing tracks database file?\n\n"+
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
                templatePath = templatePath+ "/template.db"
                
                # Copy the template database to the selected location
                import shutil
                shutil.copyfile(templatePath, filename)
                
                self.databaseCon = sqlite3.connect(str(filename))
                self.databaseCon.row_factory = sqlite3.Row
                self.settings.setValue("database/lastfile", QtCore.QVariant(filename))
        
        # Open the database
        #self.databaseCon = sqlite3.connect("tracks.db")
        #self.databaseCon.row_factory = sqlite3.Row
        
        
        
        
        
        
        
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.setWindowTitle("tracks.cute")
        
        
        
        # Get the current user
        if self.settings.contains("database/user"):
            self.current_user_id = int(self.settings.value("database/user").toString())
        else:
            self.current_user_id = False
            self.tabWidget.setCurrentIndex(8)
        
        
        # Setup the refreshables dictionary, a list of all refreshable elements 
        # on each tab
        self.hometabid=0
        self.projectstabid = 2
        self.contextstabid = 3
        self.donetabid = 6
        self.settingstabid = 8
        self.refreshables={}
        for a in range(self.tabWidget.count()):
            self.refreshables[a]=[]
        self.tabWidget.currentChanged.connect(self.refreshTab)
        
        
        # Setup the home page
        self.homeContexts = {}
        # dict for remembering which contexts have been expanded/collapsed.
        self.homeContextExpanded = {} 
        self.setupHomePage()
        
        
        # NOTE Setup the starred page
        # NOTE Starred actions are those tagged with "starred"
        # Add each of the contexts with starred items
        # TODO
        # Add the deferred/pending starred actions
        # TODO
        # Add the hidden starred actions
        # TODO
        # Add the completed starred actions
#        sql = "SELECT todos.id, todos.description, contexts.name, projects.name\
#              FROM (todos LEFT JOIN contexts ON todos.context_id = contexts.id)\
#              LEFT JOIN projects on todos.project_id = projects.id where todos.\
#              state='completed' order by todos.completed_at"
#        tracksAList = TracksActionList(
#            self.databaseCon,"Completed Actions tagged with 'starred'",sql,True)
#        self.starred_mainpane_layout.addWidget(tracksAList)
#        self.starred_mainpane_layout.addItem(
#            QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum,
#                              QtGui.QSizePolicy.Expanding))
        # Add the action editor
        self.starred_actionEditor = TracksActionEditor(self.databaseCon)
        self.starred_sidepane_layout.addWidget(self.starred_actionEditor)
        self.starred_sidepane_layout.addItem(
        QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
        
        # Setup the projects page
        self.setupProjectsPage()

        
        # Setup the contexts page
        self.setupContextsPage()
        
        
        # NOTE Setup the calendar page
        self.calendar_actionEditor = TracksActionEditor(self.databaseCon)
        self.calendar_sidepane_layout.addWidget(self.calendar_actionEditor)
        self.calendar_sidepane_layout.addItem(
        QtGui.QSpacerItem(
                1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
        
        
        # NOTE Setup the tickler page
        self.setupTicklerPage()
        
        # NOTE Setup the done page
        self.setupDonePage()
        
        # NOTE Setup the settings page
        self.setupSettingsPage()
        
        # enable the appropriate tabs
        self.tabWidget.setTabEnabled(1, False)
        self.tabWidget.setTabEnabled(4, False)
        self.tabWidget.setTabEnabled(5, False)
        #self.tabWidget.setTabEnabled(6, False)
        self.tabWidget.setTabEnabled(7, False)
        #self.tabWidget.setTabEnabled(8, False)
        self.refreshCurrentTab()
    
    def isWindowsCompositionEnabled(self):
		
        value = c_long(False)
        point = pointer(value)
        windll.dwmapi.DwmIsCompositionEnabled(point)
        return bool(value.value)
    
    def paintEvent(self, e):
        # This is a fix for the vista background transparency.
        if self.doWinComposite:
            p = QtGui.QPainter(self)
            p.setCompositionMode(QtGui.QPainter.CompositionMode_DestinationIn)
            p.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 0))

        QtGui.QMainWindow.paintEvent(self,e)
    
    def setupHomePage(self):
        """Performs initial setup of the homepage.
        
        Creates permanent widgets, but not dynamic ones"""
        logging.info("tracks->setupHomePage()")
        
        # Create the action editor
        self.actionEditor = TracksActionEditor(self.databaseCon)
        self.verticalLayout_6.addWidget(self.actionEditor)
        # Add a vertical spacer under action editor
        spacerItem1 = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem1)
        self.refreshables[self.hometabid].append(self.actionEditor)
        
        # Add the recently completed list of actions
        #sqlCompleted = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
        #               projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
        #               todos.context_id = contexts.id) LEFT JOIN projects on \
        #               todos.project_id = projects.id where todos.state=\
        #               'completed' order by todos.completed_at DESC limit 7"
        #tracksCList = TracksActionList(
        #    self.databaseCon,"Recently Completed Actions",sqlCompleted,False)
        #tracksCList.setDisplayCompletedAt(True)
        #self.verticalLayout_4.addWidget(tracksCList)
        #tracksCList.editAction.connect(self.actionEditor.setCurrentActionID)
        #tracksCList.gotoProject.connect(self.gotoProject)
        #self.refreshables[self.hometabid].append(tracksCList)
        
        # Add a vertical spacer
        spacerItem = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        
        # Connect the action editor
        #tracksCList.editAction.connect(self.actionEditor.setCurrentActionID)
        
        self.actionEditor.actionModified.connect(self.refreshCurrentTab)
        #tracksCList.actionModified.connect(self.refreshCurrentTab)
        
    def refreshHomePage(self):
        """Refreshes complex bits of the home page. Others components are refreshed via refreshables"""
        logging.info("tracks->refreshHomePage()")
        
        # get the current states of each context view
        for key in self.homeContexts.keys():
            self.homeContextExpanded[key] = self.homeContexts[key].isExpanded()
        
        # remove all the existing lists from the display
        for key in self.homeContexts.keys():
            self.homeContexts[key].hide()
            self.verticalLayout_4.removeWidget(self.homeContexts[key])
        
        
        
        # add the completed actions
        expanded = False
        if self.homeContextExpanded.has_key("completed"):
            expanded = self.homeContextExpanded["completed"]    
        sqlCompleted = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id AND todos.user_id=contexts.user_id) LEFT JOIN projects on \
                       todos.project_id = projects.id AND todos.user_id=projects.user_id where todos.state=\
                       'completed' AND todos.user_id=%s order by todos.completed_at DESC limit 7" % (self.current_user_id)
        tracksCList = TracksActionList(self.databaseCon,"Recently Completed Actions",sqlCompleted,expanded)
        self.homeContexts["completed"] = tracksCList
        tracksCList.setDisplayCompletedAt(True)
        self.verticalLayout_4.insertWidget(0,tracksCList)
        tracksCList.editAction.connect(self.actionEditor.setCurrentActionID)
        tracksCList.gotoProject.connect(self.gotoProject)
        tracksCList.editAction.connect(self.actionEditor.setCurrentActionID)
        tracksCList.actionModified.connect(self.refreshCurrentTab)
        tracksCList.refresh()
            
        # Add all of the active contexts
        #activeContextQuery = "SELECT DISTINCT contexts.id, contexts.name FROM (todos LEFT JOIN contexts ON \
        #          todos.context_id = contexts.id) LEFT JOIN projects on\
        #          todos.project_id = projects.id where todos.state='active' and projects.state = 'active' and contexts.hide='f' and (todos.show_from<=DATE('now', 'localtime') or todos.show_from IS null) ORDER BY contexts.name"
        
        activeContextQuery = "SELECT DISTINCT contexts.id, contexts.name FROM (todos LEFT JOIN contexts ON \
                  todos.context_id = contexts.id AND todos.user_id=contexts.user_id) LEFT JOIN projects on\
                  todos.project_id = projects.id AND todos.user_id=projects.user_id where\
                  todos.state='active' and \
                  projects.state = 'active' and \
                  contexts.hide='f' and \
                  (todos.show_from<=DATE('now', 'localtime') or todos.show_from IS null) and\
                  todos.id not in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active'))\
                  AND todos.user_id = %s \
                  ORDER BY contexts.name" % (self.current_user_id)
        
        for row in self.databaseCon.execute(activeContextQuery):
            expanded = True
            if self.homeContextExpanded.has_key(row[0]):
                expanded = self.homeContextExpanded[row[0]]
            
            sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                  projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                  todos.context_id = contexts.id AND todos.user_id=contexts.user_id) LEFT JOIN projects on \
                  todos.project_id = projects.id AND todos.user_id=projects.user_id where contexts.id='%s' and \
                  todos.id not in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active')) and\
                  todos.state='active' and projects.state = 'active' and (todos.show_from<=DATE('now', 'localtime') or todos.show_from IS null) \
                  AND todos.user_id=%s ORDER BY todos.due, todos.description" % (row[0],self.current_user_id)
            tracksAList = TracksActionList(self.databaseCon,"@"+row[1],sql,expanded)
            self.verticalLayout_4.insertWidget(0,tracksAList)
            
            self.homeContexts[row[0]] = tracksAList
            
            tracksAList.editAction.connect(self.actionEditor.setCurrentActionID)    
            tracksAList.actionModified.connect(self.refreshCurrentTab)
            tracksAList.gotoProject.connect(self.gotoProject)
            
            tracksAList.refresh()
         
        self.actionEditor.setCurrentUser(self.current_user_id)
        
    
    def setupProjectsPage(self):
        """Setup the projects page"""
        
        # Active projects
        self.activeProjectsList = TracksProjectList(self.databaseCon, "Active Projects", None, True)
        self.projects_mainpane_layout.addWidget(self.activeProjectsList)
        
        # Hidden projects
        self.hiddenProjectsList = TracksProjectList(self.databaseCon, "Hidden Projects", None, False)
        self.projects_mainpane_layout.addWidget(self.hiddenProjectsList)
        
        # Completed Projects
        self.completedProjectsList = TracksProjectList(self.databaseCon, "Completed Projects", None, False)
        self.projects_mainpane_layout.addWidget(self.completedProjectsList)
        
        # Expanderiser
        self.projects_mainpane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
        
        # Add the project editor
        self.projects_Editor = TracksProjectEditor(self.databaseCon)
        self.projects_sidepane_layout.addWidget(self.projects_Editor)
        self.projects_sidepane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
        #Connect lists to editor
        self.activeProjectsList.editProject.connect(self.projects_Editor.setCurrentProjectID)
        self.hiddenProjectsList.editProject.connect(self.projects_Editor.setCurrentProjectID)
        self.completedProjectsList.editProject.connect(self.projects_Editor.setCurrentProjectID)
        
        #Connect project save event to refresh lists
        self.projects_Editor.projectModified.connect(self.refreshCurrentTab)
        
        # Connect goto project
        self.activeProjectsList.gotoProject.connect(self.gotoProject)
        self.hiddenProjectsList.gotoProject.connect(self.gotoProject)
        self.completedProjectsList.gotoProject.connect(self.gotoProject)
        
        
        ###############
        # Setup the project details page
        
        # Action editor
        # Create the action editor
        self.projectview_actionEditor = TracksActionEditor(self.databaseCon)
        self.projectDetails_sidepane_layout.addWidget(self.projectview_actionEditor)
        # Add a vertical spacer under action editor
        spacerItem1 = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.projectDetails_sidepane_layout.addItem(spacerItem1)
        self.refreshables[self.projectstabid].append(self.projectview_actionEditor)
        self.projectview_actionEditor.actionModified.connect(self.refreshCurrentTab)
        
        
        self.projectBackButton.clicked.connect(self.backToProjectList)
        # Active actions
        sqlActive = None
        self.projectview_tracksAList = TracksActionList(
            self.databaseCon,"Active Actions",sqlActive,True)
        self.projectview_verticalLayout.addWidget( self.projectview_tracksAList)
        self.projectview_tracksAList.editAction.connect(self.projectview_actionEditor.setCurrentActionID)
        self.projectview_tracksAList.actionModified.connect(self.refreshCurrentTab)
        #self.refreshables[self.projectstabid].append( self.projectview_tracksAList)
        
        # Deferred actions
        sqlDeferred = None
        self.projectview_tracksDList = TracksActionList(
            self.databaseCon,"Deferred/Pending Actions",sqlDeferred,False)
        self.projectview_tracksDList.setDisplayShowFrom(True)
        self.projectview_verticalLayout.addWidget(self.projectview_tracksDList)
        self.projectview_tracksDList.editAction.connect(self.projectview_actionEditor.setCurrentActionID)
        self.projectview_tracksDList.actionModified.connect(self.refreshCurrentTab)
        #self.refreshables[self.projectstabid].append(self.projectview_tracksDList)
        
        # Complete actions
        sqlCompleted = None
        self.projectview_tracksCList = TracksActionList(
            self.databaseCon,"Completed Actions",sqlCompleted,False)
        self.projectview_tracksCList.setDisplayCompletedAt(True)
        self.projectview_verticalLayout.addWidget(self.projectview_tracksCList)
        self.projectview_tracksCList.editAction.connect(self.projectview_actionEditor.setCurrentActionID)
        self.projectview_tracksCList.actionModified.connect(self.refreshCurrentTab)
        #self.refreshables[self.projectstabid].append(self.projectview_tracksCList)
    
        # Expander
        self.projectview_verticalLayout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
    
    def refreshProjectsPage(self):
        logging.info("tracks->refreshProjectsPage")
        
        # Are listing all projects, or are we on a specifi project page?
        if self.stackedWidget_2.currentIndex() == 0:
            # Active projects
            queryActive = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                    todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                    WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                    projects LEFT JOIN todos ON projects.id=todos.project_id AND projects.user_id=todos.user_id\
                    WHERE projects.state='active' and projects.user_id=%s GROUP BY projects.id ORDER BY projects.name" %(self.current_user_id)
            self.activeProjectsList.setDBQuery(queryActive)
            
            # Hidden projects
            queryHidden = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                    todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                    WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                    projects LEFT JOIN todos ON projects.id=todos.project_id AND projects.user_id=todos.user_id \
                    WHERE projects.state='hidden' and projects.user_id=%s GROUP BY projects.id ORDER BY projects.name" % (self.current_user_id)
            self.hiddenProjectsList.setDBQuery(queryHidden)
            
            # Completed Projects
            queryCompleted = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                            todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                            WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM\
                            projects LEFT JOIN todos ON projects.id=\
                            todos.project_id AND projects.user_id=todos.user_id WHERE projects.state='completed' and projects.user_id=%s \
                            GROUP BY projects.id ORDER BY projects.name" % (self.current_user_id)
            self.completedProjectsList.setDBQuery(queryCompleted)
            
            self.projects_Editor.setCurrentUser(self.current_user_id)
        else:
            self.projectview_tracksAList.refresh()
            self.projectview_tracksDList.refresh()
            self.projectview_tracksCList.refresh()
            
            self.projectview_actionEditor.setCurrentUser(self.current_user_id)
        
        
    def gotoProject(self, projID):
        logging.info("tracks->gotoProject(" + str(projID) +")")
        
        self.tabWidget.setCurrentIndex(self.projectstabid)
        self.stackedWidget_2.setCurrentIndex(1)
        
        titleDescQuery = "SELECT projects.name, projects.description, (SELECT name from contexts where id = projects.default_context_id), projects.default_tags FROM projects WHERE projects.id = " + str(projID)
        for row in self.databaseCon.execute(titleDescQuery):
            self.projectLabel.setText("  "+str(row[0]))
            self.projectDescription.setText(str(row[1]))
            self.projectview_actionEditor.setDefaultProject(row[0])
            self.projectview_actionEditor.setDefaultContext(row[2])
            self.projectview_actionEditor.setDefaultTags(row[3])
        self.projectview_actionEditor.cancelButtonClicked()    
        
        
        self.projectview_tracksAList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state='active' \
                       AND todos.id not in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active')) \
                       AND (show_from IS NULL OR show_from <= DATETIME('now')) AND todos.project_id= "+ str(projID) + " order by todos.due, todos.description")
        
        self.projectview_tracksDList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND \
                       (show_from > DATETIME('now') OR todos.id in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active')))\
                       AND todos.project_id= "+ str(projID) + " order by todos.show_from, todos.description")
        
        self.projectview_tracksCList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'completed' AND todos.project_id= "+ str(projID) + " order by todos.completed_at DESC, todos.description")
        
        self.projectview_actionEditor.setCurrentUser(self.current_user_id)
        
    def backToProjectList(self):
        logging.info("tracks->backToProjectList()")
        self.stackedWidget_2.setCurrentIndex(0)
    
    def setupContextsPage(self):
        """Setup the contexts page"""
        # Active Contexts
        self.activeContextsList = TracksContextList(self.databaseCon, "Visible Contexts", None, True)
        self.contexts_mainpane_layout.addWidget(self.activeContextsList)
                
        # Hidden Contexts
        self.hiddenContextsList = TracksContextList(self.databaseCon, "Hidden Contexts", None, False)
        self.contexts_mainpane_layout.addWidget(self.hiddenContextsList)
        
        # Expanderiser
        self.contexts_mainpane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
        # Add the context editor
        self.contexts_Editor = TracksContextEditor(self.databaseCon)
        self.contexts_sidepane_layout.addWidget(self.contexts_Editor)
        self.contexts_sidepane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
        #Connect lists to editor
        self.activeContextsList.editContext.connect(self.contexts_Editor.setCurrentContextID)
        self.hiddenContextsList.editContext.connect(self.contexts_Editor.setCurrentContextID)
        
        # Connect goto context
        self.activeContextsList.gotoContext.connect(self.gotoContext)
        self.hiddenContextsList.gotoContext.connect(self.gotoContext)
        
        #Connect
        self.contexts_Editor.contextModified.connect(self.refreshCurrentTab)
        
        
        ### Setup the context details page
         # Create the action editor
        self.contextview_actionEditor = TracksActionEditor(self.databaseCon)
        self.contextDetails_sidepane_layout.addWidget(self.contextview_actionEditor)
        # Add a vertical spacer under action editor
        spacerItem1 = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.contextDetails_sidepane_layout.addItem(spacerItem1)
        self.refreshables[self.contextstabid].append(self.contextview_actionEditor)
        self.contextview_actionEditor.actionModified.connect(self.refreshCurrentTab)
        
        # back button
        self.contextBackButton.clicked.connect(self.backToContextList)
        
        # Active actions
        sqlActive = None
        self.contextview_tracksAList = TracksActionList(
            self.databaseCon,"Active Actions",sqlActive,True)
        self.contextview_verticalLayout.addWidget( self.contextview_tracksAList)
        self.contextview_tracksAList.editAction.connect(self.contextview_actionEditor.setCurrentActionID)
        self.contextview_tracksAList.actionModified.connect(self.refreshCurrentTab)
        #self.refreshables[self.contextstabid].append( self.contextview_tracksAList)
        
        # Deferred actions
        sqlDeferred = None
        self.contextview_tracksDList = TracksActionList(
            self.databaseCon,"Deferred/Pending Actions",sqlDeferred,False)
        self.contextview_tracksDList.setDisplayShowFrom(True)
        self.contextview_verticalLayout.addWidget(self.contextview_tracksDList)
        self.contextview_tracksDList.editAction.connect(self.contextview_actionEditor.setCurrentActionID)
        self.contextview_tracksDList.actionModified.connect(self.refreshCurrentTab)
        #self.refreshables[self.contextstabid].append(self.contextview_tracksDList)
        
        # Complete actions
        sqlCompleted = None
        self.contextview_tracksCList = TracksActionList(
            self.databaseCon,"Completed Actions",sqlCompleted,False)
        self.contextview_tracksCList.setDisplayCompletedAt(True)
        self.contextview_verticalLayout.addWidget(self.contextview_tracksCList)
        self.contextview_tracksCList.editAction.connect(self.contextview_actionEditor.setCurrentActionID)
        self.contextview_tracksCList.actionModified.connect(self.refreshCurrentTab)
        #self.refreshables[self.contextstabid].append(self.contextview_tracksCList)
    
        # Expander
        self.contextview_verticalLayout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
    
    def refreshContextsPage(self):
        
        #Are we on the contexts list, or a specific context view
        if self.stackedWidget_3.currentIndex() ==0:
            # Active Contexts
            queryActive = "SELECT contexts.id, contexts.name, SUM(CASE WHEN \
                    todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE\
                    WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                    contexts LEFT JOIN todos ON contexts.id=todos.context_id AND contexts.user_id=todos.user_id \
                    WHERE contexts.hide='f' and contexts.user_id=%s GROUP BY contexts.id ORDER BY contexts.name" % (self.current_user_id)
            self.activeContextsList.setDBQuery(queryActive)
                    
            # Hidden Contexts
            queryHidden = "SELECT contexts.id, contexts.name, SUM(CASE WHEN \
                    todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                    WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                    contexts LEFT JOIN todos ON contexts.id=todos.context_id AND contexts.user_id=todos.user_id\
                    WHERE contexts.hide='t' and contexts.user_id=%s GROUP BY contexts.id ORDER BY contexts.name" % (self.current_user_id)
            self.hiddenContextsList.setDBQuery(queryHidden)
            
            self.contexts_Editor.setCurrentUser(self.current_user_id)
        else:
            self.contextview_tracksAList.refresh()
            self.contextview_tracksDList.refresh()
            self.contextview_tracksCList.refresh()
            self.contextview_actionEditor.setCurrentUser(self.current_user_id)
        
    def gotoContext(self, id):
        logging.info("tracks->gotoContext(" + str(id) +")")
        
        self.tabWidget.setCurrentIndex(self.contextstabid)
        self.stackedWidget_3.setCurrentIndex(1)
        
        
        titleDescQuery = "SELECT contexts.name FROM contexts WHERE contexts.id = " + str(id)
        for row in self.databaseCon.execute(titleDescQuery):
            self.contextLabel.setText("  @"+str(row[0]))
            self.contextview_actionEditor.setDefaultContext(row[0])
        self.contextview_actionEditor.cancelButtonClicked()    
        
        
        self.contextview_tracksAList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.id not in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active')) AND\
                       (show_from IS NULL OR show_from <= DATETIME('now')) AND todos.context_id= "+ str(id) + " order by todos.due, todos.description")
        
        self.contextview_tracksDList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND (show_from > DATETIME('now') OR todos.id in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active'))) \
                       AND todos.context_id= "+ str(id) + " order by todos.show_from")
        
        self.contextview_tracksCList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'completed' AND todos.context_id= "+ str(id) + " order by todos.completed_at DESC")
                       
        self.contextview_actionEditor.setCurrentUser(self.current_user_id)
    
    def backToContextList(self):
        logging.info("tracks->backToContextList()")
        self.stackedWidget_3.setCurrentIndex(0)
    
    
    def setupTicklerPage(self):
        """Setup the tickler page"""
        # Tickler actions are those that are deferred via "show_from"
        
        # Add an action editor
        self.tickler_actionEditor = TracksActionEditor(self.databaseCon)
        self.tickler_sidepane_layout.addWidget(self.tickler_actionEditor)
        self.tickler_sidepane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
    
    def setupDonePage(self):
        """Setup the done page"""
        # No editing on this page, just a list of done actions grouped by various date ranges
        self.doneFortnightActionList = TracksActionList(self.databaseCon,"Last Fortnight",None,False)
        self.doneFortnightActionList.setDisplayCompletedAt(True)
        self.doneFortnightActionList.setDisplayProjectFirst(True)
        self.done_mainpane_layout.addWidget(self.doneFortnightActionList)
        self.done_mainpane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        # TODO add date ranges, e.g. done today, done last two weeks
        
    def refreshDonePage(self):
        logging.info("tracks->refreshDonePage")
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'completed' AND todos.completed_at > DATETIME('now','-14days') AND todos.user_id=%s order by projects.name, todos.completed_at DESC" % (self.current_user_id)
        self.doneFortnightActionList.setDBQuery(sql)
    
    
    
    def setupSettingsPage(self):
        logging.info("tracks->setupSettingsPage")
        self.settingsUserSelectBox.currentIndexChanged.connect(self.settingsUserChanged)
        
    def refreshSettingsPage(self):
        logging.info("tracks->setupSettingsPage")
        # User setting
        self.settingsUserSelectBox.currentIndexChanged.disconnect(self.settingsUserChanged)
        #self.settingsUserSelectBox.setDisabled(True)
        self.settingsUserSelectBox.clear()
        data = self.databaseCon.execute("SELECT login, id FROM users ORDER BY login")
        for item in data:
            self.settingsUserSelectBox.addItem(item[0],item[1])
         
        founduser = False    
        if self.current_user_id:
            index = self.settingsUserSelectBox.findData(self.current_user_id)
            if index:
                self.settingsUserSelectBox.setCurrentIndex(index)
                founduser = True
        
        if not founduser:
            self.settingsUserSelectBox.setCurrentIndex(0)
            self.current_user_id = self.settingsUserSelectBox.itemData(0).toInt()[0]
            self.settings.setValue("database/user", QtCore.QVariant(self.current_user_id))
            
        self.settingsUserSelectBox.currentIndexChanged.connect(self.settingsUserChanged)
    
    def settingsUserChanged(self, index):
        self.current_user_id = self.settingsUserSelectBox.itemData(self.settingsUserSelectBox.currentIndex()).toInt()[0]
        self.settings.setValue("database/user", QtCore.QVariant(self.current_user_id))
    
    def refreshCurrentTab(self):
        logging.info("tracks->refreshCurrentTab")
        self.refreshTab(self.tabWidget.currentIndex())
        
    def refreshTab(self, id):
        """Refreshes all of the refreshable elements of the current tab"""
        logging.info("tracks->refreshTab - "+str(id))
        
        for element in self.refreshables[id]:
            element.refresh()
        
        # for stuff not quite as simple as hitting refresh() call a tab specific method
        if id == 0: #homepage
            self.refreshHomePage()
        elif id ==2:
            self.refreshProjectsPage()
        elif id ==3:
            self.refreshContextsPage()
        elif id ==6:
            self.refreshDonePage()
        elif id == 8:
            self.refreshSettingsPage()

        
if __name__ == "__main__":
    # Start logging, first argument sets the level.
    import logging
    import sys

    LEVELS = {'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL}

    if len(sys.argv) > 1:
        level_name = sys.argv[1]
        level = LEVELS.get(level_name, logging.NOTSET)
        logging.basicConfig(level=level)

    #logging.debug('This is a debug message')
    #logging.info('This is an info message')
    #logging.warning('This is a warning message')
    #logging.error('This is an error message')
    #logging.critical('This is a critical error message')
    
    logging.info("tracks.pyqt initialising...")
    
    app = QtGui.QApplication(sys.argv)
    
    window = Tracks()
    
    window.show()
    app.exec_()
    sys.exit()
