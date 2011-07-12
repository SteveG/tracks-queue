#!/usr/bin/env python2
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
from tracksui import Ui_MainWindow
# Import tracks widgets
from tracksActionList import TracksActionList
from tracksActionEditor import TracksActionEditor
from tracksProjectWidgets import TracksProjectList, TracksProjectEditor
from tracksContextWidgets import TracksContextList, TracksContextEditor


class Tracks(QtGui.QMainWindow, Ui_MainWindow):
    """Tracks is the main window class for tracks queue"""

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
        # Make the tabs expanding
        self.tabWidget.tabBar().setExpanding(True)
        
        # Restore window geometry
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry").toByteArray())
        
        label = QtGui.QLabel()
        label.setPixmap(QtGui.QPixmap(sys.path[0] + "/tracks.cute.small.png"))
        self.tabWidget.setCornerWidget(label,QtCore.Qt.TopRightCorner)
        self.setWindowTitle("tracks queue")

        # Get the current user
        if self.settings.contains("database/user"):
            self.current_user_id = int(self.settings.value("database/user").toString())
        else:
            self.current_user_id = False
            self.tabWidget.setCurrentIndex(8)

        # Setup the refreshables dictionary, a list of all refreshable elements
        # on each tab
        self.hometabid = 0
        self.startabid = 1
        self.projectstabid = 2
        self.contextstabid = 3
        self.calendartabid = 4
        self.ticklertabid = 5
        self.donetabid = 6
        self.statstabid = 7
        self.settingstabid = 8
        self.searchtabid = 9
        self.refreshables = {}
        for a in range(self.tabWidget.count()):
            self.refreshables[a] = []
        self.tabWidget.currentChanged.connect(self.refreshTab)


        # Setup the home page
        self.homeContexts = {}
        # dict for remembering which contexts have been expanded/collapsed.
        self.homeContextExpanded = {}
        self.setupHomePage()

        # Setup starred page
        self.setupStarredPage()

        # Setup the projects page
        self.setupProjectsPage()

        # Setup the contexts page
        self.setupContextsPage()

        # NOTE Setup the calendar page
        self.setupCalendarPage()


        # NOTE Setup the tickler page
        self.setupTicklerPage()

        # NOTE Setup the done page
        self.setupDonePage()
        
        # NOTE Setup the stats page
        self.setupStatsPage()

        # NOTE Setup the settings page
        self.setupSettingsPage()
        
        # Setup the search page
        self.setupSearchPage()
        
        # Setup the keyboard shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("alt+n"),self,self.shortcutToggleForm)
        QtGui.QShortcut(QtGui.QKeySequence("alt+t"),self,self.shortcutHome)
        QtGui.QShortcut(QtGui.QKeySequence("alt+p"),self,self.shortcutProjects)
        QtGui.QShortcut(QtGui.QKeySequence("alt+c"),self,self.shortcutContexts)
        QtGui.QShortcut(QtGui.QKeySequence("alt+k"),self,self.shortcutTickler)
        QtGui.QShortcut(QtGui.QKeySequence("alt+d"),self,self.shortcutDone)
        QtGui.QShortcut(QtGui.QKeySequence("alt+l"),self,self.shortcutCalendar)
        QtGui.QShortcut(QtGui.QKeySequence("alt+o"),self,self.shortcutShowNotes)
        QtGui.QShortcut(QtGui.QKeySequence("ctrl+p"),self,self.shortcutPrint)

        # enable the appropriate tabs
        #self.tabWidget.setTabEnabled(1, False)
        #self.tabWidget.setTabEnabled(4, False)
        #self.tabWidget.setTabEnabled(5, False)
        #self.tabWidget.setTabEnabled(6, False)
        #self.tabWidget.setTabEnabled(7, False)
        #self.tabWidget.setTabEnabled(8, False)

        # Refresh the content of the current tab
        self.refreshCurrentTab()

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

        # signal mapper
        self.focusListMapper = QtCore.QSignalMapper(self)
        self.focusListMapper.mapped[str].connect(self.homePageFocusList)

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
        tracksCList = TracksActionList(self.databaseCon, "Recently Completed Actions", sqlCompleted,expanded)
        self.homeContexts["completed"] = tracksCList
        tracksCList.setDisplayProjectFirst(True)
        tracksCList.setDisplayCompletedAt(True)
        self.verticalLayout_4.insertWidget(0, tracksCList)
        tracksCList.editAction.connect(self.actionEditor.setCurrentActionID)
        tracksCList.gotoProject.connect(self.gotoProject)
        tracksCList.gotoContext.connect(self.gotoContext)
        tracksCList.editAction.connect(self.actionEditor.setCurrentActionID)
        tracksCList.actionModified.connect(self.refreshCurrentTab)

        #tracksCList.getFocus.connect(self.homePageFocus)
        self.focusListMapper.setMapping(tracksCList, "completed")
        tracksCList.getFocus.connect(self.focusListMapper.map)

        tracksCList.refresh()

        activeContextQuery = "SELECT DISTINCT contexts.id, contexts.name FROM (todos LEFT JOIN contexts ON \
                  todos.context_id = contexts.id AND todos.user_id=contexts.user_id) LEFT JOIN projects on\
                  todos.project_id = projects.id AND todos.user_id=projects.user_id where\
                  todos.state='active' and \
                  projects.state = 'active' and \
                  contexts.hide='f' and \
                  (todos.show_from<=DATE('now', 'localtime') or todos.show_from IS null) and\
                  todos.id not in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active'))\
                  AND todos.user_id = %s \
                  ORDER BY contexts.name DESC" % (self.current_user_id)

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
                  AND todos.user_id=%s ORDER BY CASE WHEN todos.due IS null THEN 1 ELSE 0 END, todos.due, projects.name, todos.description" % (row[0], self.current_user_id)
            tracksAList = TracksActionList(self.databaseCon,"@" + row[1], sql, expanded)
            tracksAList.setDisplayProjectFirst(True)

            self.verticalLayout_4.insertWidget(0, tracksAList)

            self.homeContexts[row[0]] = tracksAList

            tracksAList.editAction.connect(self.actionEditor.setCurrentActionID)    
            tracksAList.actionModified.connect(self.refreshCurrentTab)
            tracksAList.gotoProject.connect(self.gotoProject)
            tracksAList.gotoContext.connect(self.gotoContext)


            self.focusListMapper.setMapping(tracksAList, str(row[0]))
            tracksAList.getFocus.connect(self.focusListMapper.map)

            tracksAList.refresh()

        self.actionEditor.setCurrentUser(self.current_user_id)

    def homePageFocusList(self, focuskey):
        """Focus one list on the home page"""
        logging.info("tracks->homePageFocusList()")

        # Prevent flickering as things change
        self.tabWidget.setUpdatesEnabled(False)
        # shrink all lists but the expanded list
        for key in self.homeContexts.keys():
            if str(key) != focuskey:
                self.homeContexts[key].setExpanded(False)
        # this is done after to prevent flicker
        for key in self.homeContexts.keys():
            if str(key) == focuskey:
                self.homeContexts[key].setExpanded(True)
        # Re-enable screen updates
        self.tabWidget.setUpdatesEnabled(True)

    def setupStarredPage(self):
        """Setup the starred actions page"""
        logging.info("tracks->setupStarredPage()")

        # Create the action editor
        self.starredactionEditor = TracksActionEditor(self.databaseCon)
        self.starred_sidepane_layout.addWidget(self.starredactionEditor)
        # Add a vertical spacer under action editor
        spacerItem1 = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.starred_sidepane_layout.addItem(spacerItem1)
        self.refreshables[self.startabid].append(self.starredactionEditor)

    def refreshStarredPage(self):
        """Refresh the starred actions page"""
        logging.info("tracks->refreshStarredPage()")

        # remove all the existing lists from the display
        item = self.starred_mainpane_layout.takeAt(0)
        while (item != None):
            w = item.widget()
            if w:
                w.deleteLater()
            item = self.starred_mainpane_layout.takeAt(0)

        starredQuery = "select todos.context_id,contexts.name from todos, tags, taggings, contexts where todos.context_id=contexts.id AND todos.id=taggings.taggable_id and tags.id = taggings.tag_id and tags.name='starred' AND todos.state='active' AND todos.user_id=? group by todos.context_id order by contexts.name DESC"

        for row in self.databaseCon.execute(starredQuery, (str(self.current_user_id),)):
            # All are expanded by default

            sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                  todos.context_id = contexts.id AND todos.user_id=contexts.user_id) LEFT JOIN projects on \
                  todos.project_id = projects.id AND todos.user_id=projects.user_id, tags, taggings where  \
                  contexts.id=%s AND todos.id=taggings.taggable_id AND tags.id = taggings.tag_id AND tags.name='starred' AND todos.state='active' AND \
                  todos.id not in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active')) and \
                  todos.state='active' and projects.state = 'active' and (todos.show_from<=DATE('now', 'localtime') or todos.show_from IS null)  \
                  AND todos.user_id=%s ORDER BY CASE WHEN todos.due IS null THEN 1 ELSE 0 END, todos.due, projects.name, todos.description" % (row[0], self.current_user_id)

            tracksAList = TracksActionList(self.databaseCon, "@" + row[1], sql, True)
            tracksAList.setDisplayProjectFirst(True)

            self.starred_mainpane_layout.insertWidget(0, tracksAList)

            tracksAList.editAction.connect(self.starredactionEditor.setCurrentActionID)
            tracksAList.actionModified.connect(self.refreshCurrentTab)
            tracksAList.gotoProject.connect(self.gotoProject)
            tracksAList.gotoContext.connect(self.gotoContext)

            tracksAList.refresh()
        spacerItem1 = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.starred_mainpane_layout.addItem(spacerItem1)

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
        self.completedProjectsList.setHasDoubleExpander(True)
        self.projects_mainpane_layout.addWidget(self.completedProjectsList)

        # Expanderiser
        self.projects_mainpane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))


        # Add the project editor
        self.projects_Editor = TracksProjectEditor(self.databaseCon)
        self.projects_sidepane_layout.addWidget(self.projects_Editor)
        self.projects_sidepane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        self.refreshables[self.projectstabid].append(self.projects_Editor)

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
        
        # Sub Projects (experimental)
        self.subProjectsList = TracksProjectList(self.databaseCon, "Sub-Projects", None, True)
        self.subProjectsList.setShowState(True)
        self.subProjectsList.setShowEdit(False)
        self.subProjectsList.setShowDelete(False)
        self.subProjectsList.setShowSubProject(False)
        self.subProjectsList.setHasDoubleExpander(True)
        self.projectview_verticalLayout.addWidget(self.subProjectsList)
        #self.subProjectsList.editProject.connect(self.projects_Editor.setCurrentProjectID)
        self.subProjectsList.gotoProject.connect(self.gotoProject)
        
        # Active actions
        sqlActive = None
        self.projectview_tracksAList = TracksActionList(
            self.databaseCon,"Active Actions",sqlActive,True)
        self.projectview_verticalLayout.addWidget( self.projectview_tracksAList)
        self.projectview_tracksAList.setDisplayContextFirst(True)
        self.projectview_tracksAList.editAction.connect(self.projectview_actionEditor.setCurrentActionID)
        self.projectview_tracksAList.actionModified.connect(self.refreshCurrentTab)
        self.projectview_tracksAList.gotoContext.connect(self.gotoContext)
        #self.refreshables[self.projectstabid].append( self.projectview_tracksAList)
        
        # Deferred actions
        sqlDeferred = None
        self.projectview_tracksDList = TracksActionList(
            self.databaseCon, "Deferred/Pending Actions", sqlDeferred, False)
        self.projectview_tracksDList.setDisplayShowFrom(True)
        self.projectview_tracksDList.setDisplayContextFirst(True)
        self.projectview_verticalLayout.addWidget(self.projectview_tracksDList)
        self.projectview_tracksDList.editAction.connect(self.projectview_actionEditor.setCurrentActionID)
        self.projectview_tracksDList.actionModified.connect(self.refreshCurrentTab)
        self.projectview_tracksDList.gotoContext.connect(self.gotoContext)
        #self.refreshables[self.projectstabid].append(self.projectview_tracksDList)

        # Complete actions
        sqlCompleted = None
        self.projectview_tracksCList = TracksActionList(
            self.databaseCon, "Completed Actions", sqlCompleted, False)
        self.projectview_tracksCList.setDisplayCompletedAt(True)
        self.projectview_tracksCList.setDisplayContextFirst(True)
        self.projectview_tracksCList.setHasDoubleExpander(True, 10)
        self.projectview_verticalLayout.addWidget(self.projectview_tracksCList)
        self.projectview_tracksCList.editAction.connect(self.projectview_actionEditor.setCurrentActionID)
        self.projectview_tracksCList.actionModified.connect(self.refreshCurrentTab)
        self.projectview_tracksCList.gotoContext.connect(self.gotoContext)
        #self.refreshables[self.projectstabid].append(self.projectview_tracksCList)

        # Expander
        self.projectview_verticalLayout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

    def refreshProjectsPage(self):
        """refreshes the content of the projects page"""
        logging.info("tracks->refreshProjectsPage")

        # Are listing all projects, or are we on a specifi project page?
        if self.stackedWidget_2.currentIndex() == 0:
            # Active projects
            queryActive = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                    todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                    WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                    projects LEFT JOIN todos ON projects.id=todos.project_id AND projects.user_id=todos.user_id\
                    WHERE projects.state='active' and projects.user_id=%s GROUP BY projects.id ORDER BY (CASE WHEN projects.id IN (select successor_id from dependencies where relationship_type='subproject') THEN 1 ELSE 0 END), projects.name" % (self.current_user_id)
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
                            GROUP BY projects.id ORDER BY projects.name LIMIT 10" % (self.current_user_id)
            self.completedProjectsList.setDBQuery(queryCompleted)
            queryCompleted = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                            todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                            WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM\
                            projects LEFT JOIN todos ON projects.id=\
                            todos.project_id AND projects.user_id=todos.user_id WHERE projects.state='completed' and projects.user_id=%s \
                            GROUP BY projects.id ORDER BY projects.name" % (self.current_user_id)
            self.completedProjectsList.setExpandedDBQuery(queryCompleted)

            self.projects_Editor.setCurrentUser(self.current_user_id)
        else:
            self.subProjectsList.refresh()
            self.projectview_tracksAList.refresh()
            self.projectview_tracksDList.refresh()
            self.projectview_tracksCList.refresh()

            self.projectview_actionEditor.setCurrentUser(self.current_user_id)
            self.projectview_actionEditor.refresh()


    def gotoProject(self, projID):
        """Changes the project page from a list of all projects to a detailed page of one specific project"""
        logging.info("tracks->gotoProject(" + str(projID) + ")")

        self.tabWidget.setCurrentIndex(self.projectstabid)
        self.stackedWidget_2.setCurrentIndex(1)

        titleDescQuery = "SELECT projects.name, projects.description, (SELECT name from contexts where id = projects.default_context_id), projects.default_tags FROM projects WHERE projects.id = " + str(projID)
        for row in self.databaseCon.execute(titleDescQuery):
            self.projectLabel.setText("  " + str(row[0]))
            self.projectDescription.setText(str(row[1]))
            self.projectview_actionEditor.setDefaultProject(row[0])
            self.projectview_actionEditor.setDefaultContext(row[2])
            self.projectview_actionEditor.setDefaultTags(row[3])
        self.projectview_actionEditor.cancelButtonClicked()
        
        subQuery = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                    todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                    WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                    projects LEFT JOIN todos ON projects.id=todos.project_id AND projects.user_id=todos.user_id\
                    WHERE projects.id IN (select successor_id from dependencies where predecessor_id=?) AND projects.state='active' and projects.user_id=? GROUP BY projects.id ORDER BY (CASE WHEN projects.state='active' THEN 0 WHEN projects.state='hidden' THEN 1 WHEN projects.state='completed' THEN 2 ELSE 3 END), projects.name"
        self.subProjectsList.setDBQuery_args(subQuery, (projID, self.current_user_id))
        subQuery = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                    todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                    WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                    projects LEFT JOIN todos ON projects.id=todos.project_id AND projects.user_id=todos.user_id\
                    WHERE projects.id IN (select successor_id from dependencies where predecessor_id=?) and projects.user_id=? GROUP BY projects.id ORDER BY (CASE WHEN projects.state='active' THEN 0 WHEN projects.state='hidden' THEN 1 WHEN projects.state='completed' THEN 2 ELSE 3 END), projects.name"
        self.subProjectsList.setExpandedDBQuery_args(subQuery, (projID, self.current_user_id))


        self.projectview_tracksAList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state='active' \
                       AND todos.id not in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active')) \
                       AND (show_from IS NULL OR show_from <= DATETIME('now')) AND todos.project_id= "+ str(projID) + " order by CASE WHEN todos.due IS null THEN 1 ELSE 0 END, todos.due, contexts.name, todos.description")

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
        self.projectview_actionEditor.refresh()

    def backToProjectList(self):
        """Changes the projects tab from a specific project page back to the list of all projects"""
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
        self.refreshables[self.contextstabid].append(self.contexts_Editor)

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
            self.databaseCon, "Active Actions", sqlActive, True)
        self.contextview_verticalLayout.addWidget(self.contextview_tracksAList)
        self.contextview_tracksAList.setDisplayProjectFirst(True)
        self.contextview_tracksAList.editAction.connect(self.contextview_actionEditor.setCurrentActionID)
        self.contextview_tracksAList.actionModified.connect(self.refreshCurrentTab)
        self.contextview_tracksAList.gotoProject.connect(self.gotoProject)
        #self.refreshables[self.contextstabid].append( self.contextview_tracksAList)

        # Deferred actions
        sqlDeferred = None
        self.contextview_tracksDList = TracksActionList(
            self.databaseCon, "Deferred/Pending Actions", sqlDeferred, False)
        self.contextview_tracksDList.setDisplayShowFrom(True)
        self.contextview_verticalLayout.addWidget(self.contextview_tracksDList)
        self.contextview_tracksDList.setDisplayProjectFirst(True)
        self.contextview_tracksDList.editAction.connect(self.contextview_actionEditor.setCurrentActionID)
        self.contextview_tracksDList.actionModified.connect(self.refreshCurrentTab)
        self.contextview_tracksDList.gotoProject.connect(self.gotoProject)
        #self.refreshables[self.contextstabid].append(self.contextview_tracksDList)

        # Complete actions
        sqlCompleted = None
        self.contextview_tracksCList = TracksActionList(
            self.databaseCon, "Completed Actions", sqlCompleted, False)
        self.contextview_tracksCList.setDisplayCompletedAt(True)
        self.contextview_verticalLayout.addWidget(self.contextview_tracksCList)
        self.contextview_tracksCList.setDisplayProjectFirst(True)
        self.contextview_tracksCList.setHasDoubleExpander(True, 10)
        self.contextview_tracksCList.editAction.connect(self.contextview_actionEditor.setCurrentActionID)
        self.contextview_tracksCList.actionModified.connect(self.refreshCurrentTab)
        self.contextview_tracksCList.gotoProject.connect(self.gotoProject)
        #self.refreshables[self.contextstabid].append(self.contextview_tracksCList)

        # Expander
        self.contextview_verticalLayout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

    def refreshContextsPage(self):
        """Refreshes the content of the contexts tab"""

        #Are we on the contexts list, or a specific context view
        if self.stackedWidget_3.currentIndex() == 0:
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
        """Changes the context tab from a list of all contexts to a view of a single specific context"""

        logging.info("tracks->gotoContext(" + str(id) + ")")

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
                       (show_from IS NULL OR show_from <= DATETIME('now')) AND todos.context_id= " + str(id) + " order by CASE WHEN todos.due IS null THEN 1 ELSE 0 END, todos.due, projects.name, todos.description")

        self.contextview_tracksDList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND (show_from > DATETIME('now') OR todos.id in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active'))) \
                       AND todos.context_id= " + str(id) + " order by todos.show_from")

        self.contextview_tracksCList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'completed' AND todos.context_id= " + str(id) + " order by todos.completed_at DESC")

        self.contextview_actionEditor.setCurrentUser(self.current_user_id)
        self.contextview_actionEditor.refresh()

    def backToContextList(self):
        """changes the context tab view from a specific context back to the list of all contexts"""
        logging.info("tracks->backToContextList()")
        self.stackedWidget_3.setCurrentIndex(0)

    def setupCalendarPage(self):
        """Setup the calendar page"""
        logging.info("tracks->setupCalendarPage()")

        # Setup the action editor
        self.calendar_actionEditor = TracksActionEditor(self.databaseCon)
        self.calendar_sidepane_layout.addWidget(self.calendar_actionEditor)
        self.refreshables[self.calendartabid].append(self.calendar_actionEditor)
        self.calendar_sidepane_layout.addItem(
            QtGui.QSpacerItem(
               1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        self.calendar_actionEditor.actionModified.connect(self.refreshCurrentTab)

        # Actions overdue
        self.calendar_tracksOverDueList = TracksActionList(
            self.databaseCon, "Overdue", None, True)
        self.verticalLayout_3.addWidget(self.calendar_tracksOverDueList)
        self.calendar_tracksOverDueList.setDisplayShowFrom(True)
        self.calendar_tracksOverDueList.setDisplayProjectFirst(True)
        self.calendar_tracksOverDueList.setDisplayContextFirst(True)
        self.calendar_tracksOverDueList.editAction.connect(self.calendar_actionEditor.setCurrentActionID)
        self.calendar_tracksOverDueList.actionModified.connect(self.refreshCurrentTab)
        self.calendar_tracksOverDueList.gotoProject.connect(self.gotoProject)
        self.calendar_tracksOverDueList.gotoContext.connect(self.gotoContext)

        # Actions due today
        self.calendar_tracksDTodayList = TracksActionList(
            self.databaseCon, "Due today", None, True)
        self.verticalLayout_3.addWidget(self.calendar_tracksDTodayList)
        self.calendar_tracksDTodayList.setDisplayShowFrom(True)
        self.calendar_tracksDTodayList.setDisplayProjectFirst(True)
        self.calendar_tracksDTodayList.setDisplayContextFirst(True)
        self.calendar_tracksDTodayList.editAction.connect(self.calendar_actionEditor.setCurrentActionID)
        self.calendar_tracksDTodayList.actionModified.connect(self.refreshCurrentTab)
        self.calendar_tracksDTodayList.gotoProject.connect(self.gotoProject)
        self.calendar_tracksDTodayList.gotoContext.connect(self.gotoContext)

        # Actions due this week (ending Sunday)
        self.calendar_tracksDWeekList = TracksActionList(
            self.databaseCon, "Due this week", None, True)
        self.verticalLayout_3.addWidget(self.calendar_tracksDWeekList)
        self.calendar_tracksDWeekList.setDisplayShowFrom(True)
        self.calendar_tracksDWeekList.setDisplayProjectFirst(True)
        self.calendar_tracksDWeekList.setDisplayContextFirst(True)
        self.calendar_tracksDWeekList.editAction.connect(self.calendar_actionEditor.setCurrentActionID)
        self.calendar_tracksDWeekList.actionModified.connect(self.refreshCurrentTab)
        self.calendar_tracksDWeekList.gotoProject.connect(self.gotoProject)
        self.calendar_tracksDWeekList.gotoContext.connect(self.gotoContext)

        # Actions due next week
        self.calendar_tracksDNWeekList = TracksActionList(
            self.databaseCon, "Due next week", None, True)
        self.verticalLayout_3.addWidget(self.calendar_tracksDNWeekList)
        self.calendar_tracksDNWeekList.setDisplayShowFrom(True)
        self.calendar_tracksDNWeekList.setDisplayProjectFirst(True)
        self.calendar_tracksDNWeekList.setDisplayContextFirst(True)
        self.calendar_tracksDNWeekList.editAction.connect(self.calendar_actionEditor.setCurrentActionID)
        self.calendar_tracksDNWeekList.actionModified.connect(self.refreshCurrentTab)
        self.calendar_tracksDNWeekList.gotoProject.connect(self.gotoProject)
        self.calendar_tracksDNWeekList.gotoContext.connect(self.gotoContext)

        # All other future due actions
        self.calendar_tracksDueFarList = TracksActionList(
            self.databaseCon, "Due in the future", None, False)
        self.verticalLayout_3.addWidget(self.calendar_tracksDueFarList)
        self.calendar_tracksDueFarList.setDisplayShowFrom(True)
        self.calendar_tracksDueFarList.setDisplayProjectFirst(True)
        self.calendar_tracksDueFarList.setDisplayContextFirst(True)
        self.calendar_tracksDueFarList.editAction.connect(self.calendar_actionEditor.setCurrentActionID)
        self.calendar_tracksDueFarList.actionModified.connect(self.refreshCurrentTab)
        self.calendar_tracksDueFarList.gotoProject.connect(self.gotoProject)
        self.calendar_tracksDueFarList.gotoContext.connect(self.gotoContext)
        
        # Add a spacer
        self.verticalLayout_3.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

    def refreshCalendarPage(self):
        """Refreshes the content of the calendar tab"""
        logging.info("tracks->refreshCalendarPage")
        # ensure editor has current user
        self.calendar_actionEditor.setCurrentUser(self.current_user_id)

        # refresh those overdue
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.due < DATE('now') AND todos.user_id=%s order by todos.due, projects.name" % (self.current_user_id)
        self.calendar_tracksOverDueList.setDBQuery(sql)

        # refresh those due today
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.due = DATE('now') AND todos.user_id=%s order by todos.due, projects.name" % (self.current_user_id)
        self.calendar_tracksDTodayList.setDBQuery(sql)

        # refresh those due this week (less than or equal Sunday)
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.due > DATE('now') AND todos.due <= DATE('now','weekday 0') AND todos.user_id=%s order by todos.due, projects.name" % (self.current_user_id)
        self.calendar_tracksDWeekList.setDBQuery(sql)

        # refresh those due next week
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.due > DATE('now','weekday 0') AND todos.due <= DATE('now','weekday 0', '+7 days') AND todos.user_id=%s order by todos.due, projects.name" % (self.current_user_id)
        self.calendar_tracksDNWeekList.setDBQuery(sql)

        # all other future due tasks
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.due > DATE('now','weekday 0', '+7 days') AND todos.user_id=%s order by todos.due, projects.name" % (self.current_user_id)
        self.calendar_tracksDueFarList.setDBQuery(sql)

    def setupTicklerPage(self):
        """Setup the tickler page"""
        logging.info("tracks->setupTicklerPage()")
        # Tickler actions are those that are deferred via "show_from"
        
        # Setup the action editor
        self.tickler_actionEditor = TracksActionEditor(self.databaseCon)
        self.tickler_sidepane_layout.addWidget(self.tickler_actionEditor)
        self.refreshables[self.ticklertabid].append(self.tickler_actionEditor)
        self.tickler_sidepane_layout.addItem(
            QtGui.QSpacerItem(
               1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        self.tickler_actionEditor.actionModified.connect(self.refreshCurrentTab)
        
        # Actions started today
        self.tickler_tracksSTodayList = TracksActionList(
            self.databaseCon, "Starting today", None, True)
        self.tickler_mainpane_layout.addWidget(self.tickler_tracksSTodayList)
        self.tickler_tracksSTodayList.setDisplayShowFrom(True)
        self.tickler_tracksSTodayList.setDisplayProjectFirst(True)
        self.tickler_tracksSTodayList.setDisplayContextFirst(True)
        self.tickler_tracksSTodayList.editAction.connect(self.tickler_actionEditor.setCurrentActionID)
        self.tickler_tracksSTodayList.actionModified.connect(self.refreshCurrentTab)
        self.tickler_tracksSTodayList.gotoProject.connect(self.gotoProject)
        self.tickler_tracksSTodayList.gotoContext.connect(self.gotoContext)
        
        # Actions starting this week
        self.tickler_tracksSThisWeekList = TracksActionList(
            self.databaseCon, "Starting this week", None, True)
        self.tickler_mainpane_layout.addWidget(self.tickler_tracksSThisWeekList)
        self.tickler_tracksSThisWeekList.setDisplayShowFrom(True)
        self.tickler_tracksSThisWeekList.setDisplayProjectFirst(True)
        self.tickler_tracksSThisWeekList.setDisplayContextFirst(True)
        self.tickler_tracksSThisWeekList.editAction.connect(self.tickler_actionEditor.setCurrentActionID)
        self.tickler_tracksSThisWeekList.actionModified.connect(self.refreshCurrentTab)
        self.tickler_tracksSThisWeekList.gotoProject.connect(self.gotoProject)
        self.tickler_tracksSThisWeekList.gotoContext.connect(self.gotoContext)
        
        # Actions starting next week
        self.tickler_tracksSNextWeekList = TracksActionList(
            self.databaseCon, "Starting next week", None, True)
        self.tickler_mainpane_layout.addWidget(self.tickler_tracksSNextWeekList)
        self.tickler_tracksSNextWeekList.setDisplayShowFrom(True)
        self.tickler_tracksSNextWeekList.setDisplayProjectFirst(True)
        self.tickler_tracksSNextWeekList.setDisplayContextFirst(True)
        self.tickler_tracksSNextWeekList.editAction.connect(self.tickler_actionEditor.setCurrentActionID)
        self.tickler_tracksSNextWeekList.actionModified.connect(self.refreshCurrentTab)
        self.tickler_tracksSNextWeekList.gotoProject.connect(self.gotoProject)
        self.tickler_tracksSNextWeekList.gotoContext.connect(self.gotoContext)
        
        # All other actions starting in the future
        self.tickler_tracksSFutureList = TracksActionList(
            self.databaseCon, "Starting further in the future", None, False)
        self.tickler_mainpane_layout.addWidget(self.tickler_tracksSFutureList)
        self.tickler_tracksSFutureList.setDisplayShowFrom(True)
        self.tickler_tracksSFutureList.setDisplayProjectFirst(True)
        self.tickler_tracksSFutureList.setDisplayContextFirst(True)
        self.tickler_tracksSFutureList.editAction.connect(self.tickler_actionEditor.setCurrentActionID)
        self.tickler_tracksSFutureList.actionModified.connect(self.refreshCurrentTab)
        self.tickler_tracksSFutureList.gotoProject.connect(self.gotoProject)
        self.tickler_tracksSFutureList.gotoContext.connect(self.gotoContext)
        
        # Add a spacer
        self.tickler_mainpane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
    def refreshTicklerPage(self):
        """Refresh the tickler page"""
        logging.info("tracks->refreshTicklerPage()")
        
        # ensure editor has current user
        self.tickler_actionEditor.setCurrentUser(self.current_user_id)
        
        # refresh those started today
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.show_from = DATE('now') AND todos.user_id=%s order by todos.show_from, projects.name" % (self.current_user_id)
        self.tickler_tracksSTodayList.setDBQuery(sql)
        
        # refresh those starting this week (less than or equal Sunday)
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.show_from > DATE('now') AND todos.show_from <= DATE('now','weekday 0') AND todos.user_id=%s order by todos.show_from, projects.name" % (self.current_user_id)
        self.tickler_tracksSThisWeekList.setDBQuery(sql)
        
        # refresh those starting next week
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.show_from > DATE('now','weekday 0') AND todos.show_from <= DATE('now','weekday 0', '+7 days') AND todos.user_id=%s order by todos.show_from, projects.name" % (self.current_user_id)
        self.tickler_tracksSNextWeekList.setDBQuery(sql)
        
        # all other future starting tasks
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.show_from > DATE('now','weekday 0', '+7 days') AND todos.user_id=%s order by todos.show_from, projects.name" % (self.current_user_id)
        self.tickler_tracksSFutureList.setDBQuery(sql)

    def setupDonePage(self):
        """Setup the done page"""
        # No editing on this page, just a list of done actions grouped by various date ranges
        self.doneFortnightActionList = TracksActionList(self.databaseCon, "Last Fortnight", None, True)
        self.doneFortnightActionList.setDisplayCompletedAt(True)
        self.doneFortnightActionList.setDisplayProjectFirst(True)
        self.doneFortnightActionList.setShowEdit(False)
        self.doneFortnightActionList.setShowDelete(False)
        self.doneFortnightActionList.gotoProject.connect(self.gotoProject)
        self.doneFortnightActionList.gotoContext.connect(self.gotoContext)
        self.done_mainpane_layout.addWidget(self.doneFortnightActionList)

        self.doneNextFortnightActionList = TracksActionList(self.databaseCon, "Previous Fortnight", None, False)
        self.doneNextFortnightActionList.setDisplayCompletedAt(True)
        self.doneNextFortnightActionList.setDisplayProjectFirst(True)
        self.doneNextFortnightActionList.setShowEdit(False)
        self.doneNextFortnightActionList.setShowDelete(False)
        self.doneNextFortnightActionList.gotoProject.connect(self.gotoProject)
        self.doneNextFortnightActionList.gotoContext.connect(self.gotoContext)
        self.done_mainpane_layout.addWidget(self.doneNextFortnightActionList)
        
        self.doneOlderActionList = TracksActionList(self.databaseCon, "Older", None, False)
        self.doneOlderActionList.setDisplayCompletedAt(True)
        self.doneOlderActionList.setDisplayProjectFirst(True)
        self.doneOlderActionList.setShowEdit(False)
        self.doneOlderActionList.setShowDelete(False)
        self.doneOlderActionList.gotoProject.connect(self.gotoProject)
        self.doneOlderActionList.gotoContext.connect(self.gotoContext)
        self.doneOlderActionList.setHasDoubleExpander(True, 20)
        self.done_mainpane_layout.addWidget(self.doneOlderActionList)
        


        self.done_mainpane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

    def refreshDonePage(self):
        """Refreshes the content of the done tab"""
        logging.info("tracks->refreshDonePage")
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state = \
                       'completed' AND todos.completed_at > DATETIME('now','-14 days') AND todos.user_id=%s order by projects.name, todos.completed_at DESC" % (self.current_user_id)
        self.doneFortnightActionList.setDBQuery(sql)

        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'completed' AND todos.completed_at <= DATETIME('now','-14 days') AND todos.completed_at > DATETIME('now','-28 days') AND todos.user_id=%s order by projects.name, todos.completed_at DESC" % (self.current_user_id)
        self.doneNextFortnightActionList.setDBQuery(sql)
        
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'completed' AND todos.completed_at <= DATETIME('now','-28 days') AND todos.user_id=%s order by todos.completed_at DESC" % (self.current_user_id)
        self.doneOlderActionList.setDBQuery(sql)

    def setupStatsPage(self):
        """Sets up the stats tab"""
        logging.info("tracks->setupStatsPage")
        
        # totals stats
        self.stats_totals_heading = QtGui.QLabel("<b>Totals</b>")
        self.statslayout.addWidget(self.stats_totals_heading)
        
        self.stats_totals_projects = QtGui.QLabel("You have ### projects. Of those ### are active projects, ### hidden projects and ### completed projects")
        self.statslayout.addWidget(self.stats_totals_projects)
        
        self.stats_totals_contexts = QtGui.QLabel("You have ### contexts. Of those ### are visible contexts and ### are hidden contexts")
        self.statslayout.addWidget(self.stats_totals_contexts)
        
        self.stats_totals_actions1 = QtGui.QLabel("Since your first action on ##/##/#### you have a total of ### actions. ### of these are completed.")
        self.statslayout.addWidget(self.stats_totals_actions1)
        
        self.stats_totals_actions2 = QtGui.QLabel("You have ### incomplete actions of which ### are deferred actions in the tickler and ### are dependent on the completion of other actions.")
        self.statslayout.addWidget(self.stats_totals_actions2)
        
        # Add a spacer
        self.statslayout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
    
    def refreshStatsPage(self):
        """Refreshes the content of the stats tab"""
        logging.info("tracks->setupStatsPage")
        
        # update totals
        # projects
        totalprojs = self.databaseCon.execute("select count() from projects where user_id=?", (self.current_user_id,)).fetchone()[0]
        activeprojs = self.databaseCon.execute("select count() from projects where user_id=? and state='active'", (self.current_user_id,)).fetchone()[0]
        hiddenprojs = self.databaseCon.execute("select count() from projects where user_id=? and state='hidden'", (self.current_user_id,)).fetchone()[0]
        completeprojs = self.databaseCon.execute("select count() from projects where user_id=? and state='completed'", (self.current_user_id,)).fetchone()[0]
        theString = "You have %s projects. Of those %s are active projects, %s hidden projects and %s completed projects" % (totalprojs,activeprojs,hiddenprojs,completeprojs)
        self.stats_totals_projects.setText(theString)
        
        # contexts
        totalcons = self.databaseCon.execute("select count() from contexts where user_id=?", (self.current_user_id,)).fetchone()[0]
        activecons = self.databaseCon.execute("select count() from contexts where user_id=? and hide='f'", (self.current_user_id,)).fetchone()[0]
        hiddencons = self.databaseCon.execute("select count() from contexts where user_id=? and hide='t'", (self.current_user_id,)).fetchone()[0]
        theString = "You have %s contexts. Of those %s are visible contexts and %s are hidden contexts" % (totalcons,activecons,hiddencons)
        self.stats_totals_contexts.setText(theString)
        
        # actions
        firstdate = self.databaseCon.execute("select created_at from todos where user_id=? order by created_at limit 1", (self.current_user_id,)).fetchone()[0]
        totalacts = self.databaseCon.execute("select count() from todos where user_id=?", (self.current_user_id,)).fetchone()[0]
        completeacts = self.databaseCon.execute("select count() from todos where user_id=? and state='completed'", (self.current_user_id,)).fetchone()[0]
        theString = "Since your first action on %s you have a total of %s actions. %s of these are completed." % (firstdate[0:10],totalacts,completeacts)
        self.stats_totals_actions1.setText(theString)
        
        activeacts = self.databaseCon.execute("select count() from todos where user_id=? and state='active'", (self.current_user_id,)).fetchone()[0]
        deferacts = self.databaseCon.execute("select count() from todos where user_id=? and state='active' and show_from>DATE('now')", (self.current_user_id,)).fetchone()[0]
        dependacts = self.databaseCon.execute("select count() from todos where user_id=? and state='active' and id in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active'))", (self.current_user_id,)).fetchone()[0]
        theString = "You have %s incomplete actions of which %s are deferred actions in the tickler and %s are dependent on the completion of other actions." % (activeacts,deferacts,dependacts)
        self.stats_totals_actions2.setText(theString)
    
    def setupSettingsPage(self):
        logging.info("tracks->setupSettingsPage")
        self.settingsUserSelectBox.currentIndexChanged.connect(self.settingsUserChanged)

    def refreshSettingsPage(self):
        """Refreshes the content of the settings tab"""
        logging.info("tracks->setupSettingsPage")
        # User setting
        self.settingsUserSelectBox.currentIndexChanged.disconnect(self.settingsUserChanged)
        #self.settingsUserSelectBox.setDisabled(True)
        self.settingsUserSelectBox.clear()
        data = self.databaseCon.execute("SELECT login, id FROM users ORDER BY login")
        for item in data:
            self.settingsUserSelectBox.addItem(item[0], item[1])

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

    def setupSearchPage(self):
        logging.info("tracks->setupSearchPage")
        """Setup the search page"""
        # Add the search input box
        self.searchEdit = QtGui.QLineEdit()
        self.searchEdit.textChanged.connect(self.searchKeypress)
        self.search_mainpane_layout.addWidget(self.searchEdit)
        
        # Add the action search results
        self.searchActionList = TracksActionList(self.databaseCon, "Actions", None, True)
        self.searchActionList.setDisplayCompletedAt(True)
        self.searchActionList.setDisplayProjectFirst(True)
        self.searchActionList.setShowEdit(False)
        self.searchActionList.setShowDelete(False)
        self.searchActionList.gotoProject.connect(self.gotoProject)
        self.searchActionList.gotoContext.connect(self.gotoContext)
        self.search_mainpane_layout.addWidget(self.searchActionList)
        
        # Add the project search results
        self.searchProjectsList = TracksProjectList(self.databaseCon, "Projects", None, True)
        self.searchProjectsList.setShowState(True)
        self.searchProjectsList.setShowEdit(False)
        self.searchProjectsList.setShowDelete(False)
        self.searchProjectsList.setHideWhenEmtpy(False)
        self.searchProjectsList.gotoProject.connect(self.gotoProject)
        self.search_mainpane_layout.addWidget(self.searchProjectsList)
        
        # Add layout expander
        self.search_mainpane_layout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        
        # Timer to delay database search after keypresses
        self.searchTimer = QtCore.QTimer(self)
        self.searchTimer.setSingleShot(True)
        self.searchTimer.setInterval(500)
        self.searchTimer.timeout.connect(self.searchTimeout)
        
    def refreshSearchPage(self):
        logging.info("tracks->refreshSearchPage")
        text = str(self.searchEdit.text())
        if text == "" or text =="%":
            text = "really you have this text?"
        
        # refresh the action list
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.user_id=%s and ((todos.description LIKE \"%s%%\") or (todos.notes LIKE \"%s%%\")) ORDER BY todos.description" % (self.current_user_id, text, text)
        self.searchActionList.setDBQuery(sql)
        
        # refresh the project list
        sql = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                    todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                    WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                    projects LEFT JOIN todos ON projects.id=todos.project_id AND projects.user_id=todos.user_id\
                    WHERE projects.user_id=%s AND ((projects.name LIKE \"%s%%\") or (projects.description LIKE \"%s%%\")) GROUP BY projects.id ORDER BY projects.name" % (self.current_user_id, text, text)
        self.searchProjectsList.setDBQuery(sql)
        
        self.searchEdit.setFocus()
    
    def searchKeypress(self):
        self.searchTimer.start()
    def searchTimeout(self):
        logging.info("TracksActionList->commitTimeout")
        self.refreshSearchPage()

    def refreshCurrentTab(self):
        """Refreshes the currently visible tab"""
        logging.info("tracks->refreshCurrentTab")
        self.refreshTab(self.tabWidget.currentIndex())

    def refreshTab(self, id):
        """Refreshes all of the refreshable elements of the current tab"""
        logging.info("tracks->refreshTab - " + str(id))

        # for stuff not quite as simple as hitting refresh() call a tab specific method
        if id == 0:  #homepage
            self.refreshHomePage()
        elif id == 1:  #starred tab
            self.refreshStarredPage()
        elif id == 2:
            self.refreshProjectsPage()
        elif id == 3:
            self.refreshContextsPage()
        elif id == 4:
            self.refreshCalendarPage()
        elif id == 5:
            self.refreshTicklerPage()
        elif id == 6:
            self.refreshDonePage()
        elif id == 7:
            self.refreshStatsPage()
        elif id == 8:
            self.refreshSettingsPage()
        elif id == self.searchtabid:
            self.refreshSearchPage()    

        # for elements that can simply be refreshed
        for element in self.refreshables[id]:
            element.refresh()

    #
    #Shortcut routines
    #
    
    def shortcutToggleForm(self):
        logging.info("tracks->shortcutToggleForm")
        
        id = self.tabWidget.currentIndex()
        if id == self.hometabid:
            self.actionEditor.hideButtonClicked()
        elif id == self.startabid:
            self.starredactionEditor.hideButtonClicked()
        elif id == self.projectstabid:
            if self.stackedWidget_2.currentIndex() == 0:
                self.projects_Editor.hideButtonClicked()
            else:
                self.projectview_actionEditor.hideButtonClicked()
        elif id == self.contextstabid:
            if self.stackedWidget_3.currentIndex() == 0:
                self.contexts_Editor.hideButtonClicked()
            else:
                self.contextview_actionEditor.hideButtonClicked()
        elif id == self.calendartabid:
            self.calendar_actionEditor.hideButtonClicked()
        elif id == self.ticklertabid:
            self.tickler_actionEditor.hideButtonClicked()
    
    def shortcutHome(self):
        logging.info("tracks->shortcutHome")
        self.tabWidget.setCurrentIndex(self.hometabid)
    def shortcutProjects(self):
        logging.info("tracks->shortcutProjects")
        self.tabWidget.setCurrentIndex(self.projectstabid)
    def shortcutContexts(self):
        logging.info("tracks->shortcutContexts")
        self.tabWidget.setCurrentIndex(self.contextstabid)
    def shortcutTickler(self):
        logging.info("tracks->shortcutTickler")
        self.tabWidget.setCurrentIndex(self.ticklertabid)
    def shortcutCalendar(self):
        logging.info("tracks->shortcutCalendar")
        self.tabWidget.setCurrentIndex(self.calendartabid)
    def shortcutDone(self):
        logging.info("tracks->shortcutDone")
        self.tabWidget.setCurrentIndex(self.donetabid)
    def shortcutShowNotes(self):
        logging.info("tracks->shortcutShowNotes")
        id = self.tabWidget.currentIndex()
        if id == self.hometabid:  #homepage
            for key in self.homeContexts.keys():
                self.homeContexts[key].toggleAllNotes()
        elif id == self.projectstabid and self.stackedWidget_2.currentIndex() == 1:
            self.projectview_tracksAList.toggleAllNotes()
            self.projectview_tracksDList.toggleAllNotes()
            self.projectview_tracksCList.toggleAllNotes()
        elif id == self.contextstabid and self.stackedWidget_3.currentIndex() == 1:
            self.contextview_tracksAList.toggleAllNotes()
            self.contextview_tracksDList.toggleAllNotes()
            self.contextview_tracksCList.toggleAllNotes()
        elif id == self.calendartabid:
            self.calendar_tracksDNWeekList.toggleAllNotes()
            self.calendar_tracksDTodayList.toggleAllNotes()
            self.calendar_tracksDueFarList.toggleAllNotes()
            self.calendar_tracksDWeekList.toggleAllNotes()
            self.calendar_tracksOverDueList.toggleAllNotes()
        elif id == self.ticklertabid:
            self.tickler_tracksSFutureList.toggleAllNotes()
            self.tickler_tracksSNextWeekList.toggleAllNotes()
            self.tickler_tracksSThisWeekList.toggleAllNotes()
            self.tickler_tracksSTodayList.toggleAllNotes()
        elif id == self.donetabid:
            self.doneFortnightActionList.toggleAllNotes()
            self.doneNextFortnightActionList.toggleAllNotes()
            self.doneOlderActionList.toggleAllNotes()
        elif id == self.searchtabid:
            self.searchActionList.toggleAllNotes()
    def shortcutPrint(self):
        logging.info("tracks->shortcutPrint")
        # Get the widget to print
        toPrint = None
        scaleWidget = None
        theParent = None
        theParentIndex = None
        id = self.tabWidget.currentIndex()
        if id == self.hometabid:  #homepage
            toPrint = self.scrollAreaWidgetContents_2
            scaleWidget = self.scrollArea
            theParent = self.horizontalLayout_6
            theParentIndex = 0
        elif id == self.startabid:  #starred tab
            toPrint = self.scrollAreaWidgetContents
            scaleWidget = self.starred_mainpane
            theParent = self.horizontalLayout_2
            theParentIndex = 0
        elif id == self.projectstabid:
            if self.stackedWidget_2.currentIndex() == 0:
                toPrint = self.scrollAreaWidgetContents_7
                scaleWidget = self.scrollArea_5
                theParent = self.horizontalLayout_9
                theParentIndex = 0
            else:
                toPrint = self.scrollAreaWidgetContents_4   
                scaleWidget = self.scrollArea_2
                theParent = self.verticalLayout
                theParentIndex = 2
        elif id == self.contextstabid:
            if self.stackedWidget_3.currentIndex() == 0:
                toPrint = self.scrollAreaWidgetContents_8
                scaleWidget = self.scrollArea_6
                theParent = self.horizontalLayout_10
                theParentIndex = 0
            else:
                toPrint = self.scrollAreaWidgetContents_9
                scaleWidget = self.scrollArea_7
                theParent = self.verticalLayout_2
                theParentIndex = 2
        elif id == self.calendartabid:
            toPrint = self.scrollAreaWidgetContents_6
            scaleWidget = self.scrollArea_4
            theParent = self.horizontalLayout_7
            theParentIndex = 0
        elif id == self.ticklertabid:
            toPrint = self.scrollAreaWidgetContents_3
            scaleWidget = self.tickler_mainpane
            theParent = self.horizontalLayout_3
            theParentIndex = 0
        elif id == self.donetabid:
            toPrint = self.scrollAreaWidgetContents_5
            scaleWidget = self.scrollArea_3
            theParent = self.horizontalLayout_5
            theParentIndex = 0
        elif id == self.statstabid:
            toPrint = self.scrollAreaWidgetContents_11
            scaleWidget = self.scrollArea_8
            theParent = self.horizontalLayout_15
            theParentIndex = 0
        elif id == self.settingstabid:
            return
        elif id == self.searchtabid:
            toPrint = self.scrollAreaWidgetContents_10
            scaleWidget = self.scrollArea_9
            theParent = self.horizontalLayout_16
            theParentIndex = 0
        else:
            return
            
        # Make the background white
        toPrint.setAutoFillBackground(True)
        oldback = toPrint.backgroundRole()
        toPrint.setBackgroundRole( QtGui.QPalette.Base )
        
        #print toPrint.DrawChildren
        printer = QtGui.QPrinter()
        printer.setColorMode(printer.GrayScale)
        printer.setResolution(120)
        printerDialog = QtGui.QPrintDialog(printer)
        if(printerDialog.exec_() == QtGui.QDialog.Accepted):
            painter = QtGui.QPainter(printer) 
            painter.drawText(50,30,"tracks queue print out:")

            tempWidget = QtGui.QWidget()
            tempLayout = QtGui.QVBoxLayout()
            tempWidget.setLayout(tempLayout)
            tempLayout.addWidget(scaleWidget)
            tempWidget.setFixedWidth(printer.pageRect().width())
            tempLayout.activate()

            tempWidget.show()
            
            # Do the render
            import math
            pageHeight = printer.pageRect().height()
            pageWidth =  printer.pageRect().width()
            pages =  int(math.ceil((toPrint.height()) / float(printer.pageRect().height())))
            # We make the pages overlap slightly as the render is not smart an may cut cells in half
            for i in range(0, pages):
                if i>0:printer.newPage()
                toPrint.render(painter, QtCore.QPoint(0,40), QtGui.QRegion(0,i*(pageHeight-40)-i*40,pageWidth,i*(pageHeight-40)-i*40+pageHeight-40), (QtGui.QWidget.IgnoreMask | QtGui.QWidget.DrawChildren))
            painter.end()
            
            # Restore
            theParent.insertWidget(theParentIndex,scaleWidget)
        toPrint.setBackgroundRole(oldback)
    
    def closeEvent(self, event):
        logging.info("tracks->closeEvent")
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
    
    # This style sheet is to make tracks queue look pretty for the elementary theme
    #app.setStyleSheet("\
    #QTabWidget>QLabel{\
    #    background:qlineargradient(spread:pad, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(224, 224, 224, 255), stop:1 rgba(197, 197, 197, 255) );\
    #    border-bottom: 1px solid rgba(168, 168, 168, 255);\
    #    }\
    #QTabWidget>QTabBar{\
    #    background: qlineargradient(spread:pad, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(224, 224, 224, 255), stop:1 rgba(197, 197, 197, 255) );\
    #    }")

    window = Tracks()

    window.show()
    logging.info("tracks.pyqt executing...")
    app.exec_()
    logging.info("tracks.pyqt exiting...")
    sys.exit()
