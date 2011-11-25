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
from widgetActionList import WidgetActionList
from widgetActionEditor import WidgetActionEditor

class PageProjectView(QtGui.QWidget):
    # Signals
    gotoProject = QtCore.pyqtSignal(int)
    gotoContext = QtCore.pyqtSignal(int)
    def __init__(self, parent, databaseCon):
        logging.info("PageProjectView->__init__(self, parent, databaseCon)")
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
        
        # Add the action editor form 
        self.actionEditor = WidgetActionEditor(self.databaseCon)
        self.actionEditor.setVisible(False)
        self.horizontalLayout.addWidget(self.actionEditor)
        self.actionEditor.actionModified.connect(self.refresh)
        
        # Project title and description
        self.projectTitle = QtGui.QLabel("blank title")
        font = QtGui.QFont()
        font.setPointSize(14)
        self.projectTitle.setFont(font)
        self.verticalLayout.addWidget(self.projectTitle)
        self.projectDescription = QtGui.QLabel("blank description")
        self.verticalLayout.addWidget(self.projectDescription)
        
        # The lists
        
        # Sub Projects
        self.subProjectsList = WidgetProjectList(self.databaseCon, "Sub-Projects", None, True)
        self.subProjectsList.setShowState(True)
        #self.subProjectsList.setShowEdit(False)
        self.subProjectsList.setShowDelete(False)
        self.subProjectsList.setShowSubProject(False)
        self.subProjectsList.setHasDoubleExpander(True)
        self.verticalLayout.addWidget(self.subProjectsList)
        self.subProjectsList.editProject.connect(self.projectEditor.setCurrentProjectID)
        self.subProjectsList.gotoProject.connect(self.slotGotoProject)
        
        # Active actions
        sqlActive = None
        self.activeList = WidgetActionList(
            self.databaseCon,"Active Actions",sqlActive,True)
        self.verticalLayout.addWidget( self.activeList)
        self.activeList.setDisplayContextFirst(True)
        self.activeList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.activeList.actionModified.connect(self.refresh)
        self.activeList.gotoContext.connect(self.slotGotoContext)
        #self.refreshables[self.projectstabid].append( self.activeList)

        # Deferred actions
        sqlDeferred = None
        self.deferredList = WidgetActionList(
            self.databaseCon, "Deferred/Pending Actions", sqlDeferred, False)
        self.deferredList.setDisplayShowFrom(True)
        self.deferredList.setDisplayContextFirst(True)
        self.verticalLayout.addWidget(self.deferredList)
        self.deferredList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.deferredList.actionModified.connect(self.refresh)
        self.deferredList.gotoContext.connect(self.slotGotoContext)
        #self.refreshables[self.projectstabid].append(self.projectview_tracksDList)
        
        # Complete actions
        sqlCompleted = None
        self.completedList = WidgetActionList(
            self.databaseCon, "Completed Actions", sqlCompleted, False)
        self.completedList.setDisplayCompletedAt(True)
        self.completedList.setDisplayContextFirst(True)
        self.completedList.setHasDoubleExpander(True, 10)
        self.verticalLayout.addWidget(self.completedList)
        self.completedList.editAction.connect(self.actionEditor.setCurrentActionID)
        self.completedList.actionModified.connect(self.refresh)
        self.completedList.gotoContext.connect(self.slotGotoContext)
        #self.refreshables[self.projectstabid].append(self.projectview_tracksCList)
        
        #Connect project save event to refresh lists
        self.projectEditor.projectModified.connect(self.refresh)
        
        # Add a vertical spacer
        spacerItem = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
    def refresh(self, user_id=None):
        logging.info("PageProjectView->refresh()")
        if user_id:
            self.current_user_id = user_id
        
        self.subProjectsList.refresh()
        self.activeList.refresh()
        self.deferredList.refresh()
        self.completedList.refresh()

        self.projectEditor.setCurrentUser(self.current_user_id)
        self.actionEditor.setCurrentUser(self.current_user_id)
        self.projectEditor.refresh()
        self.actionEditor.refresh()
    
    def setProject(self, id, user_id):
        """Changes the project page from a list of all projects to a detailed page of one specific project"""
        logging.info("PageProjectView->setProject(" + str(id) + ")")
        
        self.current_user_id = user_id

        #self.tabWidget.setCurrentIndex(self.projectstabid)
        #self.stackedWidget_2.setCurrentIndex(1)

        titleDescQuery = "SELECT projects.name, projects.description, (SELECT name from contexts where id = projects.default_context_id), projects.default_tags FROM projects WHERE projects.id = " + str(id)
        for row in self.databaseCon.execute(titleDescQuery):
            self.projectTitle.setText(str(row[0]))
            self.projectDescription.setText(str(row[1]))
            self.actionEditor.setDefaultProject(row[0])
            self.actionEditor.setDefaultContext(row[2])
            self.projectEditor.setDefaultParent(str(row[0]))
            #self.projectview_actionEditor.setDefaultTags(row[3])
        self.actionEditor.cancelButtonClicked()
        self.projectEditor.cancelButtonClicked()
        
        subQuery = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                    todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                    WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                    projects LEFT JOIN todos ON projects.id=todos.project_id AND projects.user_id=todos.user_id\
                    WHERE projects.id IN (select successor_id from dependencies where predecessor_id=?) AND projects.state='active' and projects.user_id=? GROUP BY projects.id ORDER BY (CASE WHEN projects.state='active' THEN 0 WHEN projects.state='hidden' THEN 1 WHEN projects.state='completed' THEN 2 ELSE 3 END), projects.name"
        self.subProjectsList.setDBQuery_args(subQuery, (id, self.current_user_id))
        subQuery = "SELECT projects.id, projects.name, SUM(CASE WHEN \
                    todos.state IS 'active' THEN 1 ELSE 0 END),  SUM(CASE \
                    WHEN todos.state = 'completed' THEN 1 ELSE 0 END) FROM \
                    projects LEFT JOIN todos ON projects.id=todos.project_id AND projects.user_id=todos.user_id\
                    WHERE projects.id IN (select successor_id from dependencies where predecessor_id=?) and projects.user_id=? GROUP BY projects.id ORDER BY (CASE WHEN projects.state='active' THEN 0 WHEN projects.state='hidden' THEN 1 WHEN projects.state='completed' THEN 2 ELSE 3 END), projects.name"
        self.subProjectsList.setExpandedDBQuery_args(subQuery, (id, self.current_user_id))


        self.activeList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state='active' \
                       AND todos.id not in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active')) \
                       AND (show_from IS NULL OR show_from <= DATETIME('now')) AND todos.project_id= "+ str(id) + " order by CASE WHEN todos.due IS null THEN 1 ELSE 0 END, todos.due, contexts.name, todos.description")

        self.deferredList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'active' AND \
                       (show_from > DATETIME('now') OR todos.id in (select successor_id from dependencies where predecessor_id in (select id from todos where state='active')))\
                       AND todos.project_id= "+ str(id) + " order by todos.show_from, todos.description")

        self.completedList.setDBQuery("SELECT todos.id, todos.description, todos.state, contexts.id, contexts.name, \
                       projects.id, projects.name FROM (todos LEFT JOIN contexts ON \
                       todos.context_id = contexts.id) LEFT JOIN projects on \
                       todos.project_id = projects.id where todos.state=\
                       'completed' AND todos.project_id= "+ str(id) + " order by todos.completed_at DESC, todos.description")

        #self.projectview_actionEditor.setCurrentUser(self.current_user_id)
        #self.projectview_actionEditor.refresh()
        
    def setFormVisible(self, visible):
        logging.info("PageProjectView->setFormVisible(self, visible)")
        
        print self.actionEditor.isVisible(), self.projectEditor.isVisible()
        if self.actionEditor.isVisible():
            self.actionEditor.cancelButtonClicked()
            self.projectEditor.setVisible(visible)
            self.projectEditor.setFocus()
        elif self.projectEditor.isVisible():
            self.projectEditor.cancelButtonClicked()
            self.actionEditor.setVisible(visible)
            self.actionEditor.setFocus()
        else:
            self.actionEditor.setVisible(visible)
            self.actionEditor.setFocus()
        
    def slotGotoProject(self, id):
        logging.info("PageProjectView->slotGotoProject(self, id)")
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
        logging.info("PageProjectView->moveExclusiveExpandDown(self)")

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
        logging.info("PageProjectView->moveFocusUp")
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
        logging.info("PageProjectView->moveFocusDown")
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
