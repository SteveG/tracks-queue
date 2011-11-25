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
from widgetActionEditor import WidgetActionEditor
from widgetActionList import WidgetActionList

class PageCalendar(QtGui.QWidget):
    # Signals
    gotoProject = QtCore.pyqtSignal(int)
    gotoContext = QtCore.pyqtSignal(int)
    
    def __init__(self, parent, databaseCon):
        logging.info("PageCalendar->__init__(self, parent, databaseCon)")
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
        
        # Add the lists
        # Actions overdue
        self.overDueList = WidgetActionList(
            self.databaseCon, "Overdue", None, True)
        self.verticalLayout.addWidget(self.overDueList)
        self.overDueList.setDisplayShowFrom(True)
        self.overDueList.setDisplayProjectFirst(True)
        self.overDueList.setDisplayContextFirst(True)
        self.overDueList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.overDueList.actionModified.connect(self.refresh)
        self.overDueList.gotoProject.connect(self.slotGotoProject)
        self.overDueList.gotoContext.connect(self.slotGotoContext)

        # Actions due today
        self.dueTodayList = WidgetActionList(
            self.databaseCon, "Due today", None, True)
        self.verticalLayout.addWidget(self.dueTodayList)
        self.dueTodayList.setDisplayShowFrom(True)
        self.dueTodayList.setDisplayProjectFirst(True)
        self.dueTodayList.setDisplayContextFirst(True)
        self.dueTodayList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.dueTodayList.actionModified.connect(self.refresh)
        self.dueTodayList.gotoProject.connect(self.slotGotoProject)
        self.dueTodayList.gotoContext.connect(self.slotGotoContext)

        # Actions due this week (ending Sunday)
        self.dueWeekList = WidgetActionList(
            self.databaseCon, "Due this week", None, True)
        self.verticalLayout.addWidget(self.dueWeekList)
        self.dueWeekList.setDisplayShowFrom(True)
        self.dueWeekList.setDisplayProjectFirst(True)
        self.dueWeekList.setDisplayContextFirst(True)
        self.dueWeekList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.dueWeekList.actionModified.connect(self.refresh)
        self.dueWeekList.gotoProject.connect(self.slotGotoProject)
        self.dueWeekList.gotoContext.connect(self.slotGotoContext)

        # Actions due next week
        self.dueNextWeekList = WidgetActionList(
            self.databaseCon, "Due next week", None, True)
        self.verticalLayout.addWidget(self.dueNextWeekList)
        self.dueNextWeekList.setDisplayShowFrom(True)
        self.dueNextWeekList.setDisplayProjectFirst(True)
        self.dueNextWeekList.setDisplayContextFirst(True)
        self.dueNextWeekList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.dueNextWeekList.actionModified.connect(self.refresh)
        self.dueNextWeekList.gotoProject.connect(self.slotGotoProject)
        self.dueNextWeekList.gotoContext.connect(self.slotGotoContext)

        # All other future due actions
        self.dueFarList = WidgetActionList(
            self.databaseCon, "Due in the future", None, False)
        self.verticalLayout.addWidget(self.dueFarList)
        self.dueFarList.setDisplayShowFrom(True)
        self.dueFarList.setDisplayProjectFirst(True)
        self.dueFarList.setDisplayContextFirst(True)
        self.dueFarList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.dueFarList.actionModified.connect(self.refresh)
        self.dueFarList.gotoProject.connect(self.slotGotoProject)
        self.dueFarList.gotoContext.connect(self.slotGotoContext)
        
     
        
        
        # Add a vertical spacer
        spacerItem = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
        self.current_user_id = None
        
    def refresh(self, userId=None):
        logging.info("PageCalendar->refresh()")
        if userId:
            self.current_user_id = userId
        
        # refresh those overdue
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.due < DATE('now') AND todos.user_id=%s order by todos.due, projects.name" % (self.current_user_id)
        self.overDueList.setDBQuery(sql)

        # refresh those due today
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.due = DATE('now') AND todos.user_id=%s order by todos.due, projects.name" % (self.current_user_id)
        self.dueTodayList.setDBQuery(sql)

        # refresh those due this week (less than or equal Sunday)
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.due > DATE('now') AND todos.due <= DATE('now','weekday 0') AND todos.user_id=%s order by todos.due, projects.name" % (self.current_user_id)
        self.dueWeekList.setDBQuery(sql)

        # refresh those due next week
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.due > DATE('now','weekday 0') AND todos.due <= DATE('now','weekday 0', '+7 days') AND todos.user_id=%s order by todos.due, projects.name" % (self.current_user_id)
        self.dueNextWeekList.setDBQuery(sql)

        # all other future due tasks
        sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND todos.due > DATE('now','weekday 0', '+7 days') AND todos.user_id=%s order by todos.due, projects.name" % (self.current_user_id)
        self.dueFarList.setDBQuery(sql)


        self.actionEditor.setCurrentUser(self.current_user_id)
    
        
    def setFormVisible(self, visible):
        logging.info("PageCalendar->setFormVisible(self, visible)")
        self.actionEditor.setVisible(visible)
        self.actionEditor.setFocus()
        
    def slotGotoProject(self, id):
        logging.info("PageCalendar->slotGotoProject(self, id)")
        self.emit(QtCore.SIGNAL("gotoProject(int)"), id)
        
    def slotGotoContext(self, id):
        logging.info("PageCalendar->slotGotoContext(self, id)")
        self.emit(QtCore.SIGNAL("gotoContext(int)"), id)
    
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
        logging.info("PageCalendar->moveExclusiveExpandDown(self)")

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
        logging.info("PageCalendar->moveFocusUp")
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
        logging.info("PageCalendar->moveFocusDown")
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
