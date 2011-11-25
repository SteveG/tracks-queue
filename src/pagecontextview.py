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

from widgetActionList import WidgetActionList
from widgetActionEditor import WidgetActionEditor

class PageContextView(QtGui.QWidget):
    # Signals
    gotoProject = QtCore.pyqtSignal(int)
    
    def __init__(self, parent, databaseCon):
        logging.info("PageContextView->__init__(self, parent, databaseCon)")
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
        
        # Add the action editor form 
        self.actionEditor = WidgetActionEditor(self.databaseCon)
        self.actionEditor.setVisible(False)
        self.horizontalLayout.addWidget(self.actionEditor)
        self.actionEditor.actionModified.connect(self.refresh)
        
        # Context title
        self.contextTitle = QtGui.QLabel("blank title")
        font = QtGui.QFont()
        font.setPointSize(14)
        self.contextTitle.setFont(font)
        self.verticalLayout.addWidget(self.contextTitle)
        
        # The lists
        
        # Active actions
        sqlActive = None
        self.activeList = WidgetActionList(
            self.databaseCon,"Active Actions",sqlActive,True)
        self.verticalLayout.addWidget( self.activeList)
        self.activeList.setDisplayProjectFirst(True)
        self.activeList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.activeList.actionModified.connect(self.refresh)
        self.activeList.gotoProject.connect(self.gotoProject)
        #self.refreshables[self.projectstabid].append( self.activeList)

        # Deferred actions
        sqlDeferred = None
        self.deferredList = WidgetActionList(
            self.databaseCon, "Deferred/Pending Actions", sqlDeferred, False)
        self.deferredList.setDisplayShowFrom(True)
        self.deferredList.setDisplayProjectFirst(True)
        self.verticalLayout.addWidget(self.deferredList)
        self.deferredList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.deferredList.actionModified.connect(self.refresh)
        self.deferredList.gotoProject.connect(self.gotoProject)
        #self.refreshables[self.projectstabid].append(self.projectview_tracksDList)
        
        # Complete actions
        sqlCompleted = None
        self.completedList = WidgetActionList(
            self.databaseCon, "Completed Actions", sqlCompleted, False)
        self.completedList.setDisplayCompletedAt(True)
        self.completedList.setDisplayProjectFirst(True)
        self.completedList.setHasDoubleExpander(True, 10)
        self.verticalLayout.addWidget(self.completedList)
        self.completedList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.completedList.actionModified.connect(self.refresh)
        self.completedList.gotoProject.connect(self.gotoProject)
        #self.refreshables[self.projectstabid].append(self.projectview_tracksCList)

        
        # Add a vertical spacer
        spacerItem = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
        self.current_user_id = None
        
    def refresh(self, user_id=None):
        logging.info("PageContextView->refresh()")
        if user_id:
            self.current_user_id = user_id
            
        self.activeList.refresh()
        self.deferredList.refresh()
        self.completedList.refresh()

        self.actionEditor.setCurrentUser(self.current_user_id)
    
    def setContext(self, id, user_id=None):
        """Changes the project page from a list of all projects to a detailed page of one specific project"""
        logging.info("PageContextView->setProject(" + str(id) + ")")
        if user_id:
            self.current_user_id = user_id

        #self.tabWidget.setCurrentIndex(self.projectstabid)
        #self.stackedWidget_2.setCurrentIndex(1)

        titleDescQuery = "SELECT contexts.name FROM contexts WHERE contexts.id = " + str(id)
        for row in self.databaseCon.execute(titleDescQuery):
            self.contextTitle.setText(str(row[0]))
            #self.projectview_actionEditor.setDefaultProject(row[0])
            self.actionEditor.setDefaultContext(str(row[0]))
            #self.projectview_actionEditor.setDefaultTags(row[3])
        self.actionEditor.cancelButtonClicked()


        self.activeList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.id not in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active')) AND\
                       (show_from IS NULL OR show_from <= DATETIME('now')) AND todos.context_id= " + str(id) + " order by CASE WHEN todos.due IS null THEN 1 ELSE 0 END, todos.due, projects.name, todos.description")

        
        self.deferredList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND (show_from > DATETIME('now') OR todos.id in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active'))) \
                       AND todos.context_id= " + str(id) + " order by todos.show_from")

        self.completedList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'completed' AND todos.context_id= " + str(id) + " order by todos.completed_at DESC")

        self.actionEditor.setCurrentUser(self.current_user_id)
        self.actionEditor.refresh()
        
    def setFormVisible(self, visible):
        logging.info("PageContextView->setFormVisible(self, visible)")
        self.actionEditor.setVisible(visible)
        self.actionEditor.setFocus()
        
    def slotGotoProject(self, id):
        logging.info("PageContextView->slotGotoProject(self, id)")
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
        logging.info("PageContextView->moveExclusiveExpandDown(self)")

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
        logging.info("PageContextView->moveFocusUp")
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
        logging.info("PageContextView->moveFocusDown")
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
