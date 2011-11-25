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



from PyQt4 import QtCore, QtGui
import logging
import sys

class WidgetProjectList(QtGui.QWidget):
    """
    Provides an expandable list of GTD projects
    """
    # TODO define signals emitted by this widget
    __pyqtSignals__ = ("editProject(int)",
                     "deleteProject(int)",
                     "gotoProject(int)"
                     )
    editProject = QtCore.pyqtSignal(int)
    deleteProject = QtCore.pyqtSignal(int)
    gotoProject = QtCore.pyqtSignal(int)
    
    
    def __init__(self, databaseCon, title, dbQuery, startExpanded):
        logging.info("TracksProjectList initiated...")
        self.iconPath = str(sys.path[0])+"/icons/"
        
        self.databaseCon = databaseCon
        self.dbQuery = dbQuery
        
        QtGui.QWidget.__init__(self)
        
        # Display Options
        self.show_edit = True
        self.show_delete = True
        self.show_state = False
        self.show_subproject = True
        self.hide_when_emtpy = True
        
        # Create Layout
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        # expander button layout
        hozLayout = QtGui.QHBoxLayout()
        hozLayout.setSpacing(0)
        hozLayout.setMargin(0)
        self.verticalLayout.addLayout(hozLayout)
        
        # Create expander button
        self.toggleListButton = QtGui.QPushButton(self)
        self.toggleListButton.setText(title)
        self.toggleListButton.setStyleSheet("text-align:left;")
        self.toggleListButton.setCheckable(True)
        buttonIcon = None
        self.expanded = startExpanded
        if startExpanded:
            self.toggleListButton.setChecked(True)
            if QtGui.QIcon.hasThemeIcon("go-up"):
                buttonIcon = QtGui.QIcon.fromTheme("go-up")
            else:
                buttonIcon = QtGui.QIcon(self.iconPath + "go-up.png")
        else:
            self.toggleListButton.setChecked(False)
            if QtGui.QIcon.hasThemeIcon("go-down"):
                buttonIcon = QtGui.QIcon.fromTheme("go-down")
            else:
                buttonIcon = QtGui.QIcon(self.iconPath + "go-down.png")
        self.toggleListButton.setIcon(QtGui.QIcon(buttonIcon.pixmap(16,16,1,0)))
        hozLayout.addWidget(self.toggleListButton)
        self.connect(self.toggleListButton, QtCore.SIGNAL("clicked()"), self.toggleListButtonClick)
        
        
        #EXPERIMENTAL Double Expander button, to prevent loading big lists by default
        self.doubleExpandButton = QtGui.QPushButton()
        self.doubleExpandButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        hozLayout.addWidget(self.doubleExpandButton)
        # By default double expander isn't shown
        self.doubleExpandButton.setHidden(True)
        # Double expander is not used by default
        self.hasDoubleExpander = False
        self.doubleExpandLimit = 3
        self.doubleExpand = False
        
        # Create the action list
        self.listWidget = QtGui.QListWidget(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setSelectionMode(0)
        self.listWidget.setResizeMode(QtGui.QListView.Adjust)
        self.listWidget.setUniformItemSizes(False)
        self.verticalLayout.addWidget(self.listWidget)
        if not startExpanded:
            self.listWidget.setVisible(False)
    
        # connect the toggle list butotn
        #self.connect(self.toggleListButton, QtCore.SIGNAL("clicked()"), self.toggleListButtonClick)
        self.connect(self.doubleExpandButton, QtCore.SIGNAL("clicked()"), self.doubleExpandButtonClick)
        
        # Add the project button mappers
        self.projectDeleteButtonMapper = QtCore.QSignalMapper(self)
        self.projectDeleteButtonMapper.mapped[int].connect(self.deleteProjectButtonClicked)
        self.projectEditButtonMapper = QtCore.QSignalMapper(self)
        self.projectEditButtonMapper.mapped[int].connect(self.editProjectButtonClicked)
        self.projectTextButtonMapper = QtCore.QSignalMapper(self)
        self.projectTextButtonMapper.mapped[int].connect(self.textProjectButtonClicked)
        #self.itemStarButtonMapper = QtCore.QSignalMapper(self)
        #self.itemStarButtonMapper.mapped[int].connect(self.starItemButtonClicked)
        #self.itemLabelButtonMapper = QtCore.QSignalMapper(self)
        #self.itemLabelButtonMapper.mapped[int].connect(self.labelItemButtonClicked)
        
        # Add items to the list
        self.fillList()
    
    def toggleListButtonClick(self):
        """Toggles the visibility of the list"""
        logging.info("TracksProjectList->toggleListButtonClick")
        
        buttonIcon = None
        if QtGui.QIcon.hasThemeIcon("go-up"):
            buttonIcon = QtGui.QIcon.fromTheme("go-up")
        else:
            buttonIcon = QtGui.QIcon(self.iconPath + "go-up.png")
        if self.listWidget.isVisible():
            if QtGui.QIcon.hasThemeIcon("go-down"):
                buttonIcon = QtGui.QIcon.fromTheme("go-down")
            else:
                buttonIcon = QtGui.QIcon(self.iconPath + "go-down.png")
        self.toggleListButton.setIcon(QtGui.QIcon(buttonIcon.pixmap(16,16,1,0)))
        if self.hasDoubleExpander:
            self.doubleExpandButton.setVisible(not self.listWidget.isVisible())
        self.expanded = not self.listWidget.isVisible()
        self.listWidget.setVisible(not self.listWidget.isVisible())
    
    
    def fillList(self):
        """Fill the list widget"""
        logging.info("TracksProjectList->fillList")
        if not self.dbQuery:
            return
        
        # for double expander
        query = self.dbQuery
        args = self.dbQuery_args
        if self.hasDoubleExpander:
            if self.doubleExpand:
                query = self.expandeddbQuery
                args = self.expandeddbQuery_args
        
        
        # The query needs to return [id, name, # of active tasks, # of completed tasks]
        count = 0
        rows = None
        if not self.dbQuery_args:
            rows = self.databaseCon.execute(query).fetchall()
        else:
            rows = self.databaseCon.execute(query, self.dbQuery_args).fetchall()
        
        if self.hide_when_emtpy:    
            if len(rows) == 0:
                self.setVisible(False)
            else:
                self.setVisible(True)
        
        for row in rows:
            projectID = int(row[0])
            projectName = str(row[1])
            activeTaskCount = int(row[2])
            completedTaskCount = int(row[3])
            
            # Create the project widget
            widget = QtGui.QWidget()
            horizontalLayout = QtGui.QHBoxLayout(widget)
            horizontalLayout.setContentsMargins(2, 2, -1, 0)
            horizontalLayout.setSpacing(0)
            
            # Delete Button
            if self.show_delete:
                deleteButton = QtGui.QToolButton(widget)
                deleteButton.setStyleSheet("QToolButton{border: None;}")
                deleteIcon = None
                if QtGui.QIcon.hasThemeIcon("edit-delete"):
                    deleteIcon = QtGui.QIcon.fromTheme("edit-delete")
                else:
                    deleteIcon = QtGui.QIcon(self.iconPath + "edit-delete.png")
                deleteButton.setIcon(QtGui.QIcon(deleteIcon.pixmap(16,16,1,0)))
                horizontalLayout.addWidget(deleteButton)
                self.projectDeleteButtonMapper.setMapping(deleteButton, projectID)
                deleteButton.clicked.connect(self.projectDeleteButtonMapper.map)
            
            # Edit Button
            if self.show_edit:
                editButton = QtGui.QToolButton(widget)
                editButton.setStyleSheet("QToolButton{Border: none;}")
                editIcon = None
                if QtGui.QIcon.hasThemeIcon("accessories-text-editor"):
                    editIcon = QtGui.QIcon.fromTheme("accessories-text-editor")
                else:
                    editIcon = QtGui.QIcon(self.iconPath + "accessories-text-editor.png")
                editButton.setIcon(editIcon)
                horizontalLayout.addWidget(editButton)
                self.projectEditButtonMapper.setMapping(editButton, projectID)
                editButton.clicked.connect(self.projectEditButtonMapper.map)
                # Add action time stamp data to edit button mouseover
                time_data = self.databaseCon.execute("select created_at, updated_at from projects where id=?", (projectID,)).fetchall()
                editButton.setToolTip(str("Created: " + time_data[0][0] +"\nModified: " + time_data[0][1]))
            
            # show state?
            if self.show_state:
                state = self.databaseCon.execute("select state from projects where id=?", (projectID,)).fetchone()[0]
                stateText = QtGui.QLabel()
                stateText.setText("[" + state + "] " )
                stateText.setMinimumWidth(70)
                stateText.setMaximumWidth(70)
                stateText.setStyleSheet("QLabel{border: None; Font-size: 8px; text-align:left;}")
                horizontalLayout.addWidget(stateText)
            
            # is the project a child project?
            if self.show_subproject:
                childData = self.databaseCon.execute("select projects.name from dependencies, projects where projects.id=dependencies.predecessor_id AND dependencies.successor_id=? AND dependencies.relationship_type='subproject'",(projectID,)).fetchall()
                if len(childData) > 0:
                    childText = QtGui.QLabel()
                    childText.setText("(sub-project)   ")
                    childText.setStyleSheet("QLabel{border: None; Font-size: 8px; text-align:left;}")
                    childText.setToolTip("Subordinate to: "+ str(childData[0][0]))
                    horizontalLayout.addWidget(childText)
                        
            # Project Text
            projectText = QtGui.QPushButton(widget)
            projectText.setText(projectName)
            projectText.setCursor(QtCore.Qt.PointingHandCursor)
            projectText.setStyleSheet("QPushButton{border: None;}\n\n QPushButton:hover { color: black; background-color: lightgray; }")
            horizontalLayout.addWidget(projectText)
            self.projectTextButtonMapper.setMapping(projectText, projectID)
            projectText.clicked.connect(self.projectTextButtonMapper.map)
                
            # Spacer
            spacerItem = QtGui.QSpacerItem(227, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
            horizontalLayout.addItem(spacerItem)
            
            # Task Count Text
            #+ str(activeTaskCount) +"/" + str(activeTaskCount+completedTaskCount)
            projectTaskCount = QtGui.QLabel(widget)
            projectTaskCount.setText(" (" +str(activeTaskCount)+ " active tasks, " +str(completedTaskCount)+ " completed)")
            horizontalLayout.addWidget(projectTaskCount)
            

            listitem = QtGui.QListWidgetItem(self.listWidget)
            listitem.setSizeHint(QtCore.QSize(0,28))
            self.listWidget.setItemWidget(listitem, widget)
            
            count +=1
        
        if count == 0:
            count +=1
            self.listWidget.addItem("No Projects")
        
        #self.listWidget.setFixedHeight(count*28+6)  
        # set size of the list to be exactly enough for its contents
        contentMargins = self.listWidget.getContentsMargins()
        self.listWidget.setFixedHeight(count*28+contentMargins[1]+contentMargins[3])  
    
    def deleteProjectButtonClicked(self, id):
        logging.info("TracksProjectList->deleteProjectButtonClicked  -  " + str(id))
        query = "SELECT COUNT() FROM todos WHERE project_id=?"
        related_count =  self.databaseCon.execute(query, (id,)).fetchall()[0][0]
        reallydelete = QtGui.QMessageBox.question(self, "tracks queue: Really Delete?", "Are you sure you want to delete this project and its " + str(related_count) + " actions", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        
        logging.debug("TracksContextList->deleteContextButtonClicked, reallydelete=" + str(reallydelete==QtGui.QMessageBox.Yes))
        if reallydelete==QtGui.QMessageBox.Yes:
            # Remove the related actions
            for row in self.databaseCon.execute("SELECT id FROM todos WHERE project_id=?", (id,)):
                # Remove associated dependencies
                sqlassoc = "DELETE FROM dependencies WHERE (successor_id=? OR predecessor_id=?) AND relationship_type='depends'"
                self.databaseCon.execute(sqlassoc, (row[0],row[0]))
                # Remove the action
                self.databaseCon.execute("DELETE FROM todos WHERE id=?", (row[0],))
            # Remove the project dependencies
            sqlassoc = "DELETE FROM dependencies WHERE (successor_id=? OR predecessor_id=?) AND relationship_type='subproject'"
            self.databaseCon.execute(sqlassoc, (id,id))
            # Remove the context
            self.databaseCon.execute("DELETE FROM projects WHERE id=?", (id,))	
            self.databaseCon.commit()
            self.refresh()
        
    def editProjectButtonClicked(self, id):
        logging.info("TracksProjectList->editContextButtonClicked  -  " + str(id))
        self.emit(QtCore.SIGNAL("editProject(int)"),id)
        
    def textProjectButtonClicked(self, id):
        logging.info("TracksProjectList->textContextButtonClicked  -  " + str(id))
        self.emit(QtCore.SIGNAL("gotoProject(int)"),id)
        
    def refresh(self):
        logging.info("TracksProjectList->refresh")
        self.listWidget.clear()
        self.fillList()
        
    def setDBQuery(self, query):
        logging.info("TracksProjectList->setDBQuery")
        self.dbQuery = query
        self.dbQuery_args = None
        self.expandeddbQuery = query
        self.expandeddbQuery_args = None
        self.refresh()
    def setExpandedDBQuery(self, query):
        logging.info("TracksProjectList->setDBQuery")
        self.expandeddbQuery = query
        self.expandeddbQuery_args = None
        self.refresh()
        
    def setDBQuery_args(self, query, query_args):
        logging.info("TracksProjectList->setDBQuery")
        self.dbQuery = query
        self.dbQuery_args = query_args
        self.expandeddbQuery = query
        self.expandeddbQuery_args = query_args
        self.refresh()
    def setExpandedDBQuery_args(self, query, query_args):
        logging.info("TracksProjectList->setDBQuery")
        self.expandeddbQuery = query
        self.expandeddbQuery_args = query_args
        self.refresh()
        
    def setShowState(self, setting):
        self.show_state = setting
    def setShowEdit(self, setting):
        self.show_edit = setting
    def setShowDelete(self, setting):
        self.show_delete = setting
    def setShowSubProject(self, setting):
        self.show_subproject = setting
    def setHideWhenEmtpy(self, setting):
        self.hide_when_emtpy = setting
        
    def setHasDoubleExpander(self, hasit):
        """Makes the list size limited or not size limited"""
        logging.info("TracksProjectList->setHasDoubleExpander")
        self.hasDoubleExpander = hasit
        buttonIcon = None
        if QtGui.QIcon.hasThemeIcon("go-down"):
            buttonIcon = QtGui.QIcon.fromTheme("go-down")
        else:
            buttonIcon = QtGui.QIcon(self.iconPath + "go-down.png")
        self.doubleExpandButton.setIcon(QtGui.QIcon(buttonIcon.pixmap(16,16,1,0)))
        self.doubleExpandButton.setToolTip("Expand to show all projects\nOr restrict to just "+str(self.doubleExpandLimit))
        
        if self.expanded:
            self.doubleExpandButton.setVisible(hasit)
        
        
    def doubleExpandButtonClick(self):
        """Makes the list size limited or not size limited"""
        logging.info("TracksProjectList->doubleExpandButtonClick")
        
        self.hasDoubleExpander = True
        self.doubleExpand = not self.doubleExpand
        
        # change the button icon
        buttonIcon = None
        if QtGui.QIcon.hasThemeIcon("go-down"):
            buttonIcon = QtGui.QIcon.fromTheme("go-down")
        else:
            buttonIcon = QtGui.QIcon(self.iconPath + "go-down.png")
        if self.doubleExpand:
            if QtGui.QIcon.hasThemeIcon("go-up"):
                buttonIcon = QtGui.QIcon.fromTheme("go-up")
            else:
                buttonIcon = QtGui.QIcon(self.iconPath + "go-up.png")
        self.doubleExpandButton.setIcon(QtGui.QIcon(buttonIcon.pixmap(16,16,1,0)))
        
        self.refresh() 

