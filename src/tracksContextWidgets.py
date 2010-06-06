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

class TracksContextList(QtGui.QWidget):
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
        #self.contextDeleteButtonMapper = QtCore.QSignalMapper(self)
        #self.contextDeleteButtonMapper.mapped[int].connect(self.deleteItemButtonClicked)
        self.contextEditButtonMapper = QtCore.QSignalMapper(self)
        self.contextEditButtonMapper.mapped[int].connect(self.editItemButtonClicked)
        
        
        #self.itemStarButtonMapper = QtCore.QSignalMapper(self)
        #self.itemStarButtonMapper.mapped[int].connect(self.starItemButtonClicked)
        #self.itemLabelButtonMapper = QtCore.QSignalMapper(self)
        #self.itemLabelButtonMapper.mapped[int].connect(self.labelItemButtonClicked)
        
        # Add items to the list
        self.fillList()
    
    def toggleListButtonClick(self):
        """Toggles the visibility of the list"""
        logging.info("TracksContextList->toggleListButtonClick")
        
        buttonIcon = QtGui.QIcon.fromTheme("go-up")
        if self.listWidget.isVisible():
            buttonIcon = QtGui.QIcon.fromTheme("go-down")
        self.toggleListButton.setIcon(QtGui.QIcon(buttonIcon.pixmap(16,16,1,0)))
        self.listWidget.setVisible(not self.listWidget.isVisible())
    
    
    def fillList(self):
        """Fill the list widget"""
        logging.info("TracksContextList->fillList")
        
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
            horizontalLayout.setContentsMargins(-1, 2, -1, 0)
            horizontalLayout.setSpacing(0)
            
            # Delete Button
            deleteButton = QtGui.QToolButton(widget)
            #deleteButton.setStyleSheet("border: None;")
            deleteIcon = QtGui.QIcon.fromTheme("edit-delete")
            deleteButton.setIcon(QtGui.QIcon(deleteIcon.pixmap(16,16,1,0)))
            horizontalLayout.addWidget(deleteButton)
            #self.itemDeleteButtonMapper.setMapping(deleteButton, id)
            #deleteButton.clicked.connect(self.itemDeleteButtonMapper.map)
            
            # Edit Button
            editButton = QtGui.QToolButton(widget)
            #editButton.setStyleSheet("Border: none;")
            editButton.setIcon(QtGui.QIcon.fromTheme("accessories-text-editor"))
            horizontalLayout.addWidget(editButton)
            
            # Connect Buttons
            self.contextEditButtonMapper.setMapping(editButton, projectID)
            editButton.clicked.connect(self.contextEditButtonMapper.map)
            
            # Context Text
            contextText = QtGui.QPushButton(widget)
            contextText.setText("  @" + projectName)
            contextText.setCursor(QtCore.Qt.PointingHandCursor)
            contextText.setStyleSheet("QPushButton{border: None;}\n\n QPushButton:hover { color: black; background-color: lightgray; }")
            horizontalLayout.addWidget(contextText)
            
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
        
        self.listWidget.setFixedHeight(count*28+6)  
        
    def deleteItemButtonClicked(self, id):
        logging.info("TracksContextList->deleteContextButtonClicked  -  " + str(id))
        
    def editItemButtonClicked(self, id):
        logging.info("TracksContextList->editContextButtonClicked  -  " + str(id))
        self.emit(QtCore.SIGNAL("editContext(int)"),id)
        
    def refresh(self):
        logging.info("TracksContextList->refresh")
        self.listWidget.clear()
        self.fillList()
        

class TracksContextEditor(QtGui.QGroupBox):
    """
    Provides an editor for GTD contexts
    """
    # TODO define signals emitted by this widget
    __pyqtSignals__ = ("contextModified()"
                     )
    contextModified = QtCore.pyqtSignal()
    
    
    def __init__(self, dbCon):
        logging.info("TracksContextEditor initiated...")
        # The current item id
        self.current_id = None
        self.databaseCon = dbCon
        
        QtGui.QGroupBox.__init__(self)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QtCore.QSize(250, 16777215))
        self.setMinimumSize(QtCore.QSize(250, 0))
        
        
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        
        # Hide Form Button
        self.formVisible = True
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.hideFormButton = QtGui.QPushButton(self)
        self.hideFormButton.setText("<< Hide Form")
        self.hideFormButton.setToolTip("Hide the form from view")
        self.horizontalLayout_3.addWidget(self.hideFormButton)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.hideFormButton.clicked.connect(self.hideButtonClicked)
        
        # Name line edit
        self.nameLabel = QtGui.QLabel(self)
        self.nameLabel.setText("Name")
        self.verticalLayout.addWidget(self.nameLabel)
        self.nameEdit = QtGui.QLineEdit(self)
        self.verticalLayout.addWidget(self.nameEdit)
                
        # Is context visible on front page???
        self.statusLabel = QtGui.QLabel(self)
        self.statusLabel.setText("Visible on Home Page?")
        self.verticalLayout.addWidget(self.statusLabel)
        
        self.statusLayout = QtGui.QHBoxLayout()
        self.statusRadio1 = QtGui.QRadioButton(self)
        self.statusRadio1.setText("visible")
        self.statusRadio1.setChecked(True)
        self.statusLayout.addWidget(self.statusRadio1)
        self.statusRadio2 = QtGui.QRadioButton(self)
        self.statusRadio2.setText("hidden")
        self.statusLayout.addWidget(self.statusRadio2)
        self.verticalLayout.addLayout(self.statusLayout)
        
        
        # Commit and Cancel button
        # TODO hide cancel button by default??? only show when editing an existing item
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.addProjectButton = QtGui.QPushButton(self)
        self.addProjectButton.setText("Add context")
        self.horizontalLayout_5.addWidget(self.addProjectButton)
        self.cancelEditButton = QtGui.QPushButton(self)
        self.cancelEditButton.setText("Cancel edit")
        self.cancelEditButton.setVisible(self.current_id != None)
        self.horizontalLayout_5.addWidget(self.cancelEditButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        
        # connect buttons
        self.cancelEditButton.clicked.connect(self.cancelButtonClicked)
        self.addProjectButton.clicked.connect(self.addButtonClicked)
        
        
        
    def hideButtonClicked(self):
        logging.info("TracksContextEditor->hideButtonClicked")
        self.formVisible = not self.formVisible
        if self.formVisible:
            self.hideFormButton.setText(">> Hide Form")
            self.setMaximumSize(QtCore.QSize(250, 16777215))
            self.setMinimumSize(QtCore.QSize(250, 0))
        else:
            self.hideFormButton.setText("<<")
            self.setMaximumSize(QtCore.QSize(50, 16777215))
            self.setMinimumSize(QtCore.QSize(50, 0))
        
        self.nameLabel.setVisible(self.formVisible)
        self.nameEdit.setVisible(self.formVisible)
        self.statusLabel.setVisible(self.formVisible)
        self.statusRadio1.setVisible(self.formVisible)
        self.statusRadio2.setVisible(self.formVisible)
        self.addProjectButton.setVisible(self.formVisible)
        #TODO only reshow cancel button when editing existing item
        self.cancelEditButton.setVisible(self.formVisible and self.current_id != None)
                
    
    
    def cancelButtonClicked(self):
        logging.info("TracksContextEditor->cancelButtonClicked")
        # Clear all the widgets
        # TODO also clear internal data reflecting the database item we are editing
        self.nameEdit.clear()
        self.statusRadio1.setChecked(True)
        
        self.current_id = None
        self.cancelEditButton.setVisible(False)
        self.addProjectButton.setText("Add context")

    def addButtonClicked(self):
        logging.info("TracksContextEditor->addButtonClicked")
        # Need to either save an existing context, or add a new context
        if (self.nameEdit.text()=="") or (self.statusRadio1.isChecked()==self.statusRadio2.isChecked()):
            QtGui.QMessageBox.critical(self,
                            "Error",
                            "Context editor is either incomplete or erroneous\n\nNo data has been inserted or modified")
            return
        
        # TODO add or modify the context
        name = str(self.nameEdit.text())
        hidden = 'f'
        if self.statusRadio1.isChecked():
            hidden = 'f'
        elif self.statusRadio2.isChecked():
            hidden = 't'
        
        if self.current_id == None:
            logging.debug("TracksContextEditor->addButtonClicked->adding new context")
            q = "INSERT INTO contexts VALUES(NULL,?,NULL,?,1,DATETIME('now'),DATETIME('now'))"
            self.databaseCon.execute(q,[name,hidden])
            self.databaseCon.commit()
            
            self.cancelButtonClicked()
            
            self.emit(QtCore.SIGNAL("contextModified()"))
        else:
            logging.debug("TracksContextEditor->addButtonClicked->modifying existing context")
            
            q = "UPDATE contexts SET name=?, hide=?, updated_at=DATETIME('now') WHERE id=?"
            self.databaseCon.execute(q,[name,hidden,self.current_id])
            self.databaseCon.commit()
            
            self.cancelButtonClicked()
            
            self.emit(QtCore.SIGNAL("contextModified()"))

    def setCurrentContextID(self, contextID):
        logging.info("TracksContextEditor->setCurrentContextID")
        
        for row in self.databaseCon.execute("select id, name, hide FROM contexts where id="+str(contextID)):
            self.nameEdit.setText(row[1])
            if row[2] == "f":
                self.statusRadio1.setChecked(True)
            else:
                self.statusRadio2.setChecked(True)
        
        self.current_id=contextID
        self.addProjectButton.setText("Save context")
        self.cancelEditButton.setVisible(True)
        ## Make the editor visible if not already
        if not self.formVisible:
            self.hideButtonClicked()
        
        
                
        
		