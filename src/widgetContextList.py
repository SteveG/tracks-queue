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

class WidgetContextList(QtGui.QWidget):
    """
    Provides an expandable list of GTD projects
    """
    # TODO define signals emitted by this widget
    __pyqtSignals__ = ("editContext(int)",
                     "deleteContext(int)",
                     "gotoContext(int)"
                     )
    editContext = QtCore.pyqtSignal(int)
    deleteContext = QtCore.pyqtSignal(int)
    gotoContext = QtCore.pyqtSignal(int)
    
    def __init__(self, databaseCon, title, dbQuery, startExpanded):
        logging.info("TracksContextList initiated...")
        self.iconPath = str(sys.path[0])+"/icons/"
        
        self.databaseCon = databaseCon
        self.dbQuery = dbQuery
        
        QtGui.QWidget.__init__(self)
        
        
        # Create Layout
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        
        # Create expander button
        self.toggleListButton = QtGui.QPushButton(self)
        self.toggleListButton.setText(title)
        self.toggleListButton.setStyleSheet("text-align:left;")
        self.toggleListButton.setCheckable(True)
        buttonIcon = None
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
        self.verticalLayout.addWidget(self.toggleListButton)
        self.connect(self.toggleListButton, QtCore.SIGNAL("clicked()"), self.toggleListButtonClick)
        
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
        
        # Add the item button mappers
        self.contextDeleteButtonMapper = QtCore.QSignalMapper(self)
        self.contextDeleteButtonMapper.mapped[int].connect(self.deleteItemButtonClicked)
        self.contextEditButtonMapper = QtCore.QSignalMapper(self)
        self.contextEditButtonMapper.mapped[int].connect(self.editItemButtonClicked)
        self.contextTextButtonMapper = QtCore.QSignalMapper(self)
        self.contextTextButtonMapper.mapped[int].connect(self.textContextButtonClicked)
        
        #self.itemStarButtonMapper = QtCore.QSignalMapper(self)
        #self.itemStarButtonMapper.mapped[int].connect(self.starItemButtonClicked)
        #self.itemLabelButtonMapper = QtCore.QSignalMapper(self)
        #self.itemLabelButtonMapper.mapped[int].connect(self.labelItemButtonClicked)
        
        # Add items to the list
        self.fillList()
    
    def toggleListButtonClick(self):
        """Toggles the visibility of the list"""
        logging.info("TracksContextList->toggleListButtonClick")
        
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
        self.listWidget.setVisible(not self.listWidget.isVisible())
    
    
    def fillList(self):
        """Fill the list widget"""
        logging.info("TracksContextList->fillList")
        if self.dbQuery == None:
            return
        # The query needs to return [id, name, # of active tasks, # of completed tasks]
        count = 0
        for row in self.databaseCon.execute(self.dbQuery):
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
            deleteButton = QtGui.QToolButton(widget)
            deleteButton.setStyleSheet("QToolButton{border: None;}")
            deleteIcon = None
            if QtGui.QIcon.hasThemeIcon("edit-delete"):
                deleteIcon = QtGui.QIcon.fromTheme("edit-delete")
            else:
                deleteIcon = QtGui.QIcon(self.iconPath + "edit-delete.png")
            deleteButton.setIcon(QtGui.QIcon(deleteIcon.pixmap(16,16,1,0)))
            horizontalLayout.addWidget(deleteButton)
            self.contextDeleteButtonMapper.setMapping(deleteButton, projectID)
            deleteButton.clicked.connect(self.contextDeleteButtonMapper.map)
            
            # Edit Button
            editButton = QtGui.QToolButton(widget)
            editButton.setStyleSheet("QToolButton{Border: none;}")
            editIcon = None
            if QtGui.QIcon.hasThemeIcon("accessories-text-editor"):
                editIcon = QtGui.QIcon.fromTheme("accessories-text-editor")
            else:
                editIcon = QtGui.QIcon(self.iconPath + "accessories-text-editor.png")
            editButton.setIcon(editIcon)
            horizontalLayout.addWidget(editButton)
            # Add action time stamp data to edit button mouseover
            time_data = self.databaseCon.execute("select created_at, updated_at from contexts where id=?", (projectID,)).fetchall()
            editButton.setToolTip(str("Created: " + time_data[0][0] +"\nModified: " + time_data[0][1]))
            
            # Connect Buttons
            self.contextEditButtonMapper.setMapping(editButton, projectID)
            editButton.clicked.connect(self.contextEditButtonMapper.map)
            
            # Context Text
            contextText = QtGui.QPushButton(widget)
            contextText.setText("  @" + projectName)
            contextText.setCursor(QtCore.Qt.PointingHandCursor)
            contextText.setStyleSheet("QPushButton{border: None;}\n\n QPushButton:hover { color: black; background-color: lightgray; }")
            horizontalLayout.addWidget(contextText)
            self.contextTextButtonMapper.setMapping(contextText, projectID)
            contextText.clicked.connect(self.contextTextButtonMapper.map)
            
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
            self.listWidget.addItem("No Contexts")
        
        # set size of the list to be exactly enough for its contents
        contentMargins = self.listWidget.getContentsMargins()
        self.listWidget.setFixedHeight(count*28+contentMargins[1]+contentMargins[3])  
        #self.listWidget.setFixedHeight(count*28+6)  
        
    def deleteItemButtonClicked(self, id):
        logging.info("TracksContextList->deleteContextButtonClicked  -  " + str(id))
        query = "SELECT COUNT() FROM todos WHERE context_id=?"
        related_count =  self.databaseCon.execute(query, (id,)).fetchall()[0][0]
        reallydelete = QtGui.QMessageBox.question(self, "tracks queue: Really Delete?", "Are you sure you want to delete this context and its " + str(related_count) + " actions", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        
        logging.debug("TracksContextList->deleteContextButtonClicked, reallydelete=" + str(reallydelete==QtGui.QMessageBox.Yes))
        if reallydelete==QtGui.QMessageBox.Yes:
            # Remove the related actions
            for row in self.databaseCon.execute("SELECT id FROM todos WHERE context_id=?", (id,)):
                # Remove associated dependencies
                sqlassoc = "DELETE FROM dependencies WHERE (successor_id=? OR predecessor_id=?) AND relationship_type='depends'"
                self.databaseCon.execute(sqlassoc, (row[0],row[0]))
                # Remove the action
                self.databaseCon.execute("DELETE FROM todos WHERE id=?", (row[0],))
            # Remove the context
            self.databaseCon.execute("DELETE FROM contexts WHERE id=?", (id,))	
            self.databaseCon.commit()
            self.refresh()
        
    def editItemButtonClicked(self, id):
        logging.info("TracksContextList->editContextButtonClicked  -  " + str(id))
        self.emit(QtCore.SIGNAL("editContext(int)"),id)
        
    def textContextButtonClicked(self, id):
        logging.info("TracksContextList->textContextButtonClicked  -  " + str(id))
        self.emit(QtCore.SIGNAL("gotoContext(int)"),id)
        
    def refresh(self):
        logging.info("TracksContextList->refresh")
        self.listWidget.clear()
        self.fillList()
        
    def setDBQuery(self, query):
        logging.info("TracksContextList->setDBQuery")
        self.dbQuery = query
        self.refresh()

