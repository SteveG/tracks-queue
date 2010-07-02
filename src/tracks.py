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
        
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.setWindowTitle("tracks.cute")    
        
        # Open the database
        self.databaseCon = sqlite3.connect("tracks.db")
        self.databaseCon.row_factory = sqlite3.Row
        
        # Setup the refreshables dictionary, a list of all refreshable elements 
        # on each tab
        self.hometabid=0
        self.projectstabid = 2
        self.contextstabid = 3
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
        #self.setupDonePage()
        
        self.refreshCurrentTab()
    
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
        sqlCompleted = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'completed' order by todos.completed_at DESC limit 7"
        tracksCList = TracksActionList(
            self.databaseCon,"Recently Completed Actions",sqlCompleted,False)
        self.verticalLayout_4.addWidget(tracksCList)
        tracksCList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.refreshables[self.hometabid].append(tracksCList)
        
        # Add a vertical spacer
        spacerItem = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        
        # Connect the action editor
        tracksCList.editAction.connect(self.actionEditor.setCurrentActionID)
        
        self.actionEditor.actionModified.connect(self.refreshCurrentTab)
        tracksCList.actionModified.connect(self.refreshCurrentTab)
        
    def refreshHomePage(self):
        """Refreshes complex bits of the home page. Others components are refreshed via refreshables"""
        logging.info("tracks->refreshHomePage()")
        
        # get the current states of each context view
        for key in self.homeContexts.keys():
            self.homeContextExpanded[key] = self.homeContexts[key].isExpanded()
        
        # remove all the existing dynamic lists from the display
        for key in self.homeContexts.keys():
            self.homeContexts[key].hide()
            self.verticalLayout_4.removeWidget(self.homeContexts[key])
            
        # Add all of the active contexts
        activeContextQuery = "SELECT DISTINCT contexts.id, contexts.name FROM (todos LEFT JOIN contexts ON \
                  todos.context_id = contexts.id) LEFT JOIN projects on\
                  todos.project_id = projects.id where todos.state='active' and projects.state = 'active' and contexts.hide='f' ORDER BY contexts.name"
        
        for row in self.databaseCon.execute(activeContextQuery):
            expanded = True
            if self.homeContextExpanded.has_key(row[0]):
                expanded = self.homeContextExpanded[row[0]]
            
            sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                  projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                  todos.context_id = contexts.id) LEFT JOIN projects on \
                  todos.project_id = projects.id where contexts.id='%s' and \
                  todos.state='active' and projects.state = 'active'" % row[0]
            tracksAList = TracksActionList(self.databaseCon,"@"+row[1],sql,expanded)
            self.verticalLayout_4.insertWidget(0,tracksAList)
            
            self.homeContexts[row[0]] = tracksAList
            
            tracksAList.editAction.connect(self.actionEditor.setCurrentActionID)    
            tracksAList.actionModified.connect(self.refreshCurrentTab)
    
    def setupProjectsPage(self):
        """Setup the projects page"""
        
        # Active projects
        queryActive = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                      todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                      WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                      projects LEFT JOIN todos ON projects.id=todos.project_id \
                      WHERE projects.state='active' GROUP BY projects.id"
        self.activeProjectsList = TracksProjectList(self.databaseCon, "Active Projects", queryActive, True)
        self.projects_mainpane_layout.addWidget(self.activeProjectsList)
        self.refreshables[self.projectstabid].append(self.activeProjectsList)
        
        # Hidden projects
        queryHidden = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                      todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                      WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                      projects LEFT JOIN todos ON projects.id=todos.project_id \
                      WHERE projects.state='hidden' GROUP BY projects.id"
        self.hiddenProjectsList = TracksProjectList(self.databaseCon, "Hidden Projects", queryHidden, False)
        self.projects_mainpane_layout.addWidget(self.hiddenProjectsList)
        self.refreshables[self.projectstabid].append(self.hiddenProjectsList)
        
        # Completed Projects
        queryCompleted = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                         todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                         WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM\
                         projects LEFT JOIN todos ON projects.id=\
                         todos.project_id WHERE projects.state='completed' \
                         GROUP BY projects.id"
        self.completedProjectsList = TracksProjectList(self.databaseCon, "Completed Projects", queryCompleted, False)
        self.projects_mainpane_layout.addWidget(self.completedProjectsList)
        self.refreshables[self.projectstabid].append(self.completedProjectsList)
        
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
        self.refreshables[self.projectstabid].append( self.projectview_tracksAList)
        
        # Deferred actions
        sqlDeferred = None
        self.projectview_tracksDList = TracksActionList(
            self.databaseCon,"Deferred Actions",sqlDeferred,False)
        self.projectview_verticalLayout.addWidget(self.projectview_tracksDList)
        self.projectview_tracksDList.editAction.connect(self.projectview_actionEditor.setCurrentActionID)
        self.projectview_tracksDList.actionModified.connect(self.refreshCurrentTab)
        self.refreshables[self.projectstabid].append(self.projectview_tracksDList)
        
        # Complete actions
        sqlCompleted = None
        self.projectview_tracksCList = TracksActionList(
            self.databaseCon,"Completed Actions",sqlCompleted,False)
        self.projectview_verticalLayout.addWidget(self.projectview_tracksCList)
        self.projectview_tracksCList.editAction.connect(self.projectview_actionEditor.setCurrentActionID)
        self.projectview_tracksCList.actionModified.connect(self.refreshCurrentTab)
        self.refreshables[self.projectstabid].append(self.projectview_tracksCList)
    
        # Expander
        self.projectview_verticalLayout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
    def gotoProject(self, projID):
        logging.info("tracks->gotoProject(" + str(projID) +")")
        
        self.tabWidget.setCurrentIndex(self.projectstabid)
        self.stackedWidget_2.setCurrentIndex(1)
        
        titleDescQuery = "SELECT projects.name, projects.description, (SELECT name from contexts where id = projects.default_context_id), projects.default_tags FROM projects WHERE projects.id = " + str(projID)
        for row in self.databaseCon.execute(titleDescQuery):
            self.projectLabel.setText(str(row[0]))
            self.projectDescription.setText(str(row[1]))
            self.projectview_actionEditor.setDefaultProject(row[0])
            self.projectview_actionEditor.setDefaultContext(row[2])
            self.projectview_actionEditor.setDefaultTags(row[3])
        self.projectview_actionEditor.cancelButtonClicked()    
        
        
        self.projectview_tracksAList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND (show_from IS NULL OR show_from <= DATETIME('now')) AND todos.project_id= "+ str(projID) + " order by todos.show_from DESC")
        
        self.projectview_tracksDList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND show_from > DATETIME('now') AND todos.project_id= "+ str(projID) + " order by todos.show_from DESC")
        
        self.projectview_tracksCList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'completed' AND todos.project_id= "+ str(projID) + " order by todos.completed_at DESC")
        
    def backToProjectList(self):
        logging.info("tracks->backToProjectList()")
        self.stackedWidget_2.setCurrentIndex(0)
    
    def setupContextsPage(self):
        """Setup the contexts page"""
        # Active Contexts
        queryActive = "SELECT contexts.id, contexts.name, SUM(CASE WHEN \
                      todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE\
                      WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                      contexts LEFT JOIN todos ON contexts.id=todos.context_id \
                      WHERE contexts.hide='f' GROUP BY contexts.id"
        self.activeContextsList = TracksContextList(self.databaseCon, "Visible Contexts", queryActive, True)
        self.contexts_mainpane_layout.addWidget(self.activeContextsList)
        self.refreshables[self.contextstabid].append(self.activeContextsList)
                
        # Hidden Contexts
        queryHidden = "SELECT contexts.id, contexts.name, SUM(CASE WHEN \
                      todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                      WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                      contexts LEFT JOIN todos ON contexts.id=todos.context_id \
                      WHERE contexts.hide='t' GROUP BY contexts.id"
        self.hiddenContextsList = TracksContextList(self.databaseCon, "Hidden Contexts", queryHidden, False)
        self.contexts_mainpane_layout.addWidget(self.hiddenContextsList)
        self.refreshables[self.contextstabid].append(self.hiddenContextsList)
        
        # Expanderiser
        self.contexts_mainpane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
        # Add the context editor
        self.contexts_Editor = TracksContextEditor(self.databaseCon)
        self.contexts_sidepane_layout.addWidget(self.contexts_Editor)
        self.contexts_sidepane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
        #Connect lists to editor
        self.activeContextsList.editContext.connect(self.contexts_Editor.setCurrentContextID)
        self.hiddenContextsList.editContext.connect(self.contexts_Editor.setCurrentContextID)
        
        #Connect
        self.contexts_Editor.contextModified.connect(self.refreshCurrentTab)
    
    
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
        sql = "SELECT todos.id, todos.description, contexts.name, projects.name\
              FROM (todos LEFT JOIN contexts ON todos.context_id = contexts.id)\
              LEFT JOIN projects on todos.project_id = projects.id where \
              todos.state='completed' order by todos.completed_at"
        actionList = TracksActionList(self.databaseCon,"Completed Actions'",sql,True)
        self.done_mainpane_layout.addWidget(actionList)
        self.done_mainpane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        # TODO add date ranges, e.g. done today, done last two weeks
    
    def refreshCurrentTab(self):
        self.refreshTab(self.tabWidget.currentIndex())
        
    def refreshTab(self, id):
        """Refreshes all of the refreshable elements of the current tab"""
        logging.info("tracks->refreshTab")
        
        for element in self.refreshables[id]:
            element.refresh()
        
        # for stuff not quite as simple as hitting refresh() call a tab specific method
        if id == 0: #homepage
            self.refreshHomePage()

        
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
