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

"""
Provides an expandable list of GTD actions
"""

from PyQt4 import QtCore, QtGui
import logging

class TracksActionList(QtGui.QWidget):
    # TODO define signals emitted by this widget
    __pyqtSignals__ = ("editAction(int)",
                     "starAction(int)",
                     "deleteAction(int)",
                     "completeAction(int)",
                     "gotoLabel(QString)"
                     )
    editAction = QtCore.pyqtSignal(int)
    starAction = QtCore.pyqtSignal(int)
    deleteAction = QtCore.pyqtSignal(int)
    completeAction = QtCore.pyqtSignal(int)
    gotoLabel = QtCore.pyqtSignal(QtCore.QString)

    # Need to add a list title, a database query, an option for expanded or not
    def __init__(self, databaseCon, title, dbQuery, startExpanded):
        logging.info("TracksActionList initiated...")
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
            buttonIcon = QtGui.QIcon.fromTheme("go-up")
        else:
            self.toggleListButton.setChecked(False)
            buttonIcon = QtGui.QIcon.fromTheme("go-down")
        self.toggleListButton.setIcon(QtGui.QIcon(buttonIcon.pixmap(16,16,1,0)))
        self.verticalLayout.addWidget(self.toggleListButton)
        
        
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
        self.connect(self.toggleListButton, QtCore.SIGNAL("clicked()"), self.toggleListButtonClick)
        
        # Add the item button mappers
        self.itemDeleteButtonMapper = QtCore.QSignalMapper(self)
        self.itemDeleteButtonMapper.mapped[int].connect(self.deleteItemButtonClicked)
        self.itemEditButtonMapper = QtCore.QSignalMapper(self)
        self.itemEditButtonMapper.mapped[int].connect(self.editItemButtonClicked)
        self.itemStarButtonMapper = QtCore.QSignalMapper(self)
        self.itemStarButtonMapper.mapped[int].connect(self.starItemButtonClicked)
        self.itemLabelButtonMapper = QtCore.QSignalMapper(self)
        self.itemLabelButtonMapper.mapped[int].connect(self.labelItemButtonClicked)
        
        # Add items to the list
        self.fillList()
        
        # Resize items in the list and then resize the list.
        #h = 0
        #for a in range(self.listWidget.count()):
        #   i = self.listWidget.item(a)
        #   i.setSizeHint(QtCore.QSize(0,22))
        #   h += self.listWidget.sizeHintForRow(a)
        #self.listWidget.setFixedHeight(h+6)
    
    def isExpanded(self):
        """Returns a boolean indicating whether the list is expanded or not"""
        return self.listWidget.isVisible()
    
    def toggleListButtonClick(self):
        """Toggles the visibility of the list"""
        logging.info("TracksActionList->toggleListButtonClick")
        
        buttonIcon = QtGui.QIcon.fromTheme("go-up")
        if self.listWidget.isVisible():
            buttonIcon = QtGui.QIcon.fromTheme("go-down")
        self.toggleListButton.setIcon(QtGui.QIcon(buttonIcon.pixmap(16,16,1,0)))
        self.listWidget.setVisible(not self.listWidget.isVisible())
    
    # The nominated query is expexted to return a table of the following form:
    # action id, action description, #TODO complete this
    def fillList(self):
        """Fill the list widget"""
        logging.info("TracksActionList->fillList")
        numberOfItems = 6
        
        count = 0
        if self.dbQuery == None:
            self.dbQuery = "select id, description, 0, 0 from todos order by description"
        for row in self.databaseCon.execute(self.dbQuery):
            id = row[0]
            desc = row[1]
            context = row[2]
            if context == 0:
                context = None
            project = row[3]
            if project == 0:
                project = None

        #for a in range(numberOfItems):
            widget = QtGui.QWidget()
            horizontalLayout = QtGui.QHBoxLayout(widget)
            horizontalLayout.setContentsMargins(-1, 2, -1, 0)
            horizontalLayout.setSpacing(2)
            
            # Delete Button
            deleteButton = QtGui.QToolButton(widget)
            #deleteButton.setStyleSheet("border: None;")
            deleteIcon = QtGui.QIcon.fromTheme("edit-delete")
            deleteButton.setIcon(QtGui.QIcon(deleteIcon.pixmap(16,16,1,0)))
            #deleteButton.setMaximumSize(QtCore.QSize(16,16)) #TEST
            horizontalLayout.addWidget(deleteButton)
            self.itemDeleteButtonMapper.setMapping(deleteButton, id)
            deleteButton.clicked.connect(self.itemDeleteButtonMapper.map)
            
            # Edit Button
            editButton = QtGui.QToolButton(widget)
            #editButton.setStyleSheet("Border: none;")
            editButton.setIcon(QtGui.QIcon.fromTheme("accessories-text-editor"))
            #editButton.setMaximumSize(QtCore.QSize(25,25)) #TEST
            horizontalLayout.addWidget(editButton)
            self.itemEditButtonMapper.setMapping(editButton, id)
            editButton.clicked.connect(self.itemEditButtonMapper.map)
            
            # Star Button
            starButton = QtGui.QToolButton(widget)
            #starButton.setStyleSheet("border: None;")
            importantIcon = QtGui.QIcon.fromTheme("emblem-important")
            starButton.setIcon(QtGui.QIcon(importantIcon.pixmap(16,16,1,0)))
            #starButton.setMaximumSize(QtCore.QSize(16,16)) #TEST
            horizontalLayout.addWidget(starButton)
            self.itemStarButtonMapper.setMapping(starButton, id)
            starButton.clicked.connect(self.itemStarButtonMapper.map)
            
            # Check Box
            checkBox = QtGui.QCheckBox(widget)
            checkBox.setText("")
            #checkBox.setMaximumSize(QtCore.QSize(12,12)) #TEST
            horizontalLayout.addWidget(checkBox)
            #TODO make this do something
            
            # Action Text
            actionText = QtGui.QLabel(widget)
            actionText.setText(desc)
            horizontalLayout.addWidget(actionText)
            
            # Label Button
            labelButton = QtGui.QPushButton(widget)
            font = QtGui.QFont()
            font.setPointSize(7)
            labelButton.setFont(font)
            labelButton.setText("fishing")
            labelButton.setCursor(QtCore.Qt.PointingHandCursor)
            labelButton.setStyleSheet("background-color: lightblue; border: None;")
            horizontalLayout.addWidget(labelButton)
            self.itemLabelButtonMapper.setMapping(labelButton, id) #TODO fix
            labelButton.clicked.connect(self.itemLabelButtonMapper.map)
            
            # Add Context Button #TODO make this optional
            if context != None:
                contextButton = QtGui.QPushButton(widget)
                font = QtGui.QFont()
                font.setPointSize(7)
                contextButton.setFont(font)
                contextButton.setText("[c]")
                contextButton.setToolTip("context: @" + context)
                contextButton.setCursor(QtCore.Qt.PointingHandCursor)
                contextButton.setStyleSheet("border: None;")
                horizontalLayout.addWidget(contextButton)
                
            # Add project button #TODO make this optional
            if project != None:
                projectButton = QtGui.QPushButton(widget)
                font = QtGui.QFont()
                font.setPointSize(7)
                projectButton.setFont(font)
                projectButton.setText("[p]")
                projectButton.setToolTip("project: " + project)
                projectButton.setCursor(QtCore.Qt.PointingHandCursor)
                projectButton.setStyleSheet("border: None;")
                horizontalLayout.addWidget(projectButton)
            
            # Spacer
            spacerItem = QtGui.QSpacerItem(227, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
            horizontalLayout.addItem(spacerItem)
            
            
            listitem = QtGui.QListWidgetItem(self.listWidget)
            listitem.setSizeHint(QtCore.QSize(0,22))
            self.listWidget.setItemWidget(listitem, widget)
                
                
            count+=1
        
        if count == 0:
            count +=1
            self.listWidget.addItem("No Actions")
        
        self.listWidget.setFixedHeight(count*22+6)  
            
    def deleteItemButtonClicked(self, id):
        logging.info("TracksActionList->deleteItemButtonClicked  -  " + str(id))
        
    def editItemButtonClicked(self, id):
        logging.info("TracksActionList->editItemButtonClicked  -  " + str(id))
        self.emit(QtCore.SIGNAL("editAction(int)"),id)

        
    def starItemButtonClicked(self, id):
        logging.info("TracksActionList->starItemButtonClicked  -  " + str(id))
        
    def labelItemButtonClicked(self, id):
        logging.info("TracksActionList->labelItemButtonClicked  -  " +str(id))
        
class DumbWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
    def mousePressEvent(self, event):
        print "clicked"