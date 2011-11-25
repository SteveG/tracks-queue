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

class PageHome(QtGui.QWidget):
    # Signals
    gotoProject = QtCore.pyqtSignal(int)
    gotoContext = QtCore.pyqtSignal(int)
    
    def __init__(self, parent, databaseCon):
        logging.info("PageHome->__init__(self, parent, databaseCon)")
        QtGui.QWidget.__init__(self, parent)
        self.databaseCon = databaseCon
        #self.settings = QtCore.QSettings("tracks-queue", "tracks-queue")
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
        
        # Add a vertical spacer
        spacerItem = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
        # Set of contexts to be displayed
        self.homeContexts = {}
        
        # add the list completed actions
        sqlCompleted = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id AND todos.user_id=contexts.user_id) LEFT JOIN projects on \
                       todos.project_id = projects.id AND todos.user_id=projects.user_id where todos.state=\
                       'completed' AND todos.user_id=%s order by todos.completed_at DESC limit 7" % (2)
        completedList = WidgetActionList(self.databaseCon, "Recently Completed Actions", sqlCompleted,False)
        completedList.setDisplayProjectFirst(True)
        completedList.setDisplayCompletedAt(True)
        completedList.actionModified.connect(self.refresh)
        completedList.gotoProject.connect(self.slotGotoProject)
        completedList.gotoContext.connect(self.slotGotoContext)
        self.homeContexts["completed"] = completedList
        self.verticalLayout.insertWidget(0, completedList)
        
        self.current_user_id = None
    
       
    def refresh(self, userId=None):
        logging.info("PageHome->refresh()")
        
        if userId:
            self.current_user_id = userId
        
        # If there are new contexts that we don't already have, add them
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
        fetchedContexts = {}
        for row in self.databaseCon.execute(activeContextQuery):
            fetchedContexts[row[0]] = row[1] 
            #print len(fetchedContexts)
            if self.homeContexts.has_key(row[0]):
                None
            else:
                sql = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                  projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                  todos.context_id = contexts.id AND todos.user_id=contexts.user_id) LEFT JOIN projects on \
                  todos.project_id = projects.id AND todos.user_id=projects.user_id where contexts.id='%s' and \
                  todos.id not in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active')) and\
                  todos.state='active' and projects.state = 'active' and (todos.show_from<=DATE('now', 'localtime') or todos.show_from IS null) \
                  AND todos.user_id=%s ORDER BY CASE WHEN todos.due IS null THEN 1 ELSE 0 END, todos.due, projects.name, todos.description" % (row[0], self.current_user_id)
                tracksAList = WidgetActionList(self.databaseCon,"@" + row[1], sql, True)
                tracksAList.setDisplayProjectFirst(True)
                tracksAList.editAction.connect(self.actionEditor.setCurrentActionID)    
                tracksAList.actionModified.connect(self.refresh)
                tracksAList.gotoProject.connect(self.slotGotoProject)
                tracksAList.gotoContext.connect(self.slotGotoContext)
                self.homeContexts[row[0]]=tracksAList
                self.verticalLayout.insertWidget(len(fetchedContexts)-1,tracksAList)
                
        completed = self.homeContexts["completed"]
        sqlCompleted = "SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id AND todos.user_id=contexts.user_id) LEFT JOIN projects on \
                       todos.project_id = projects.id AND todos.user_id=projects.user_id where todos.state=\
                       'completed' AND todos.user_id=%s order by todos.completed_at DESC limit 7" % (self.current_user_id)
        completed.setDBQuery(sqlCompleted)
                
        # remove any contexts that may have been removed / hidden, refresh the others
        for key in self.homeContexts.keys():
            if key not in fetchedContexts.keys() and key != "completed":
                self.homeContexts[key].hide()
                self.verticalLayout.removeWidget(self.homeContexts[key])   
                del self.homeContexts[key] 
            else:
                self.homeContexts[key].refresh()
        
        self.actionEditor.setCurrentUser(2)
        
    def setFormVisible(self, visible):
        logging.info("PageHome->setFormVisible(self, visible)")
        self.actionEditor.setVisible(visible)
        self.actionEditor.setFocus()
        
    def slotGotoProject(self, id):
        logging.info("PageHome->slotGotoProject(self, id)")
        self.emit(QtCore.SIGNAL("gotoProject(int)"), id)
        
    def slotGotoContext(self, id):
        logging.info("PageHome->slotGotoContext(self, id)")
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
        logging.info("PageHome->moveExclusiveExpandDown(self)")

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
        logging.info("PageHome->moveFocusUp")
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
        logging.info("PageHome->moveFocusDown")
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
