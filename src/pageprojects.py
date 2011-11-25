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
from widgetProjectEditor import WidgetProjectEditor
from widgetProjectList import WidgetProjectList

class PageProjects(QtGui.QWidget):
    # Signals
    gotoProject = QtCore.pyqtSignal(int)
    def __init__(self, parent, databaseCon):
        logging.info("PageProjects->__init__(self, parent, databaseCon)")
        QtGui.QWidget.__init__(self, parent)
        self.databaseCon = databaseCon
        self.settings = QtCore.QSettings("tracks-queue", "tracks-queue")
        #latitudeLabel = QtGui.QLabel("Latitude:")
        #layout = QtGui.QGridLayout(self)
        #layout.addWidget(latitudeLabel, 0, 0)
        
        # The main page layout
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        
        # Scroll area for lists
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        
        # Layout for scroll area
        widget = QtGui.QWidget()
        self.scrollArea.setWidget(widget)
        self.verticalLayout = QtGui.QVBoxLayout(widget)
        
        self.horizontalLayout.addWidget(self.scrollArea)      
        
        # Add the project editor form 
        self.projectEditor = WidgetProjectEditor(self.databaseCon)
        self.projectEditor.setVisible(False)        
        self.horizontalLayout.addWidget(self.projectEditor)
        self.projectEditor.projectModified.connect(self.refresh)
        
        
        # Add the project lists
        # Active projects
        self.activeProjectsList = WidgetProjectList(self.databaseCon, "Active Projects", None, True)
        self.activeProjectsList.gotoProject.connect(self.slotGotoProject)
        self.activeProjectsList.editProject.connect(self.projectEditor.setCurrentProjectID)
        self.verticalLayout.addWidget(self.activeProjectsList)
        # Hidden projects
        self.hiddenProjectsList = WidgetProjectList(self.databaseCon, "Hidden Projects", None, False)
        self.hiddenProjectsList.gotoProject.connect(self.slotGotoProject)
        self.hiddenProjectsList.editProject.connect(self.projectEditor.setCurrentProjectID)
        self.verticalLayout.addWidget(self.hiddenProjectsList)
        # Completed projects
        self.completedProjectsList = WidgetProjectList(self.databaseCon, "Completed Projects", None, False)
        self.completedProjectsList.gotoProject.connect(self.slotGotoProject)
        self.completedProjectsList.editProject.connect(self.projectEditor.setCurrentProjectID)
        self.completedProjectsList.setHasDoubleExpander(True)
        self.verticalLayout.addWidget(self.completedProjectsList)
        
        #Connect project save event to refresh lists
        self.projectEditor.projectModified.connect(self.refresh)
        
        # Add a vertical spacer
        spacerItem = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
        self.current_user_id = None
        
    def refresh(self, userId=None):
        logging.info("PageProjects->refresh()")
        if userId:
            self.current_user_id = userId
        
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

        self.projectEditor.setCurrentUser(self.current_user_id)
        self.projectEditor.refresh()
    
        
    def setFormVisible(self, visible):
        logging.info("PageProjects->setFormVisible(self, visible)")
        self.projectEditor.setVisible(visible)
        self.projectEditor.setFocus()
        
    def slotGotoProject(self, id):
        logging.info("PageProjects->slotGotoProject(self, id)")
        self.emit(QtCore.SIGNAL("gotoProject(int)"), id)
    
    def moveExclusiveExpandUp(self):
        logging.info("tracks->moveExclusiveExpandUp")

        # shrink all lists but the expanded list
        focuspos = None
        posList = {}
        for key in self.homeContexts.keys():
            pos = self.homeContexts[key].pos().y()
            posList[pos] = key
            if self.homeContexts[key].isExpanded():
                if (not focuspos) or (pos < focuspos):
                    focuspos = pos
            self.homeContexts[key].setExpanded(False)
        posKeys = posList.keys()
        posKeys.sort(reverse=True)
        done = False
        for pos in posKeys:
            if focuspos and pos<focuspos:
                self.homeContexts[posList[pos]].setExpanded(True)
                done = True
                break
        if done == False:
            self.homeContexts[posList[posKeys[len(posKeys)-1]]].setExpanded(True)
        
    def moveExclusiveExpandDown(self):
        logging.info("PageProjects->moveExclusiveExpandDown(self)")

        # shrink all lists but the expanded list
        focuspos = None
        posList = {}
        for key in self.homeContexts.keys():
            pos = self.homeContexts[key].pos().y()
            posList[pos] = key
            if self.homeContexts[key].isExpanded():
                if (not focuspos) or (pos > focuspos):
                    focuspos = pos
            self.homeContexts[key].setExpanded(False)
        posKeys = posList.keys()
        posKeys.sort()
        done = False
        
        for pos in posKeys:
            if focuspos and pos>focuspos:
                self.homeContexts[posList[pos]].setExpanded(True)
                done = True
                break
        if done == False:
            self.homeContexts[posList[posKeys[len(posKeys)-1]]].setExpanded(True)
    
    def moveFocusUp(self):
        # moves the keyboard focus up to the next expanded list
        logging.info("PageProjects->moveFocusUp")
        keyfocuspos = None
        posList = {}
        # find the list with keyboard focus if there is one
        for key in self.homeContexts.keys():
            pos = self.homeContexts[key].pos().y()
            posList[pos] = key
            if self.homeContexts[key].isAncestorOf(QtGui.QApplication.focusWidget()):
                    keyfocuspos = pos  
        # sort the lists by position
        posKeys = posList.keys()
        posKeys.sort(reverse=True)
        done = False
        # set keyboard focus on the next highest list that is expanded
        for pos in posKeys:
            if pos<keyfocuspos:
                if self.homeContexts[posList[pos]].isExpanded():
                    self.homeContexts[posList[pos]].listWidget.setFocus()
                else:
                    self.homeContexts[posList[pos]].toggleListButton.setFocus()
                done = True
                break
        # If none were expanded set to highest list and expand
        if done == False:
            if self.homeContexts[posList[posKeys[0]]].isExpanded():
                self.homeContexts[posList[posKeys[0]]].listWidget.setFocus()#setExpanded(True)
            else:
                self.homeContexts[posList[posKeys[0]]].toggleListButton.setFocus()
            
    def moveFocusDown(self):
        # moves the keyboard focus down to the next expanded list
        logging.info("PageProjects->moveFocusDown")
        keyfocuspos = None
        posList = {}
        # find the list with keyboard focus if there is one
        for key in self.homeContexts.keys():
            pos = self.homeContexts[key].pos().y()
            posList[pos] = key
            if self.homeContexts[key].isAncestorOf(QtGui.QApplication.focusWidget()):
                    keyfocuspos = pos  
        # sort the lists by position
        posKeys = posList.keys()
        posKeys.sort()
        done = False
        # set keyboard focus on the next lowest list that is expanded
        for pos in posKeys:
            if keyfocuspos and pos>keyfocuspos:
                if self.homeContexts[posList[pos]].isExpanded():
                    self.homeContexts[posList[pos]].listWidget.setFocus()
                else:
                    self.homeContexts[posList[pos]].toggleListButton.setFocus()
                done = True
                break
        # If none were expanded set to lowest list
        if done == False:
            if self.homeContexts[posList[posKeys[0]]].isExpanded():
                self.homeContexts[posList[posKeys[0]]].listWidget.setFocus()#setExpanded(True)
            else:
                self.homeContexts[posList[posKeys[0]]].toggleListButton.setFocus()
