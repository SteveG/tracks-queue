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



class WidgetContextEditor(QtGui.QGroupBox):
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
        self.current_user_id = None
        
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
        self.verticalLayout.setMargin(4)
        
        # Hide Form Button
        #self.formVisible = True
        #self.horizontalLayout_3 = QtGui.QHBoxLayout()
        #spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        #self.horizontalLayout_3.addItem(spacerItem)
        #self.hideFormButton = QtGui.QPushButton(self)
        #self.hideFormButton.setText(">> Hide Form")
        #self.hideFormButton.setToolTip("Hide the form from view")
        #self.horizontalLayout_3.addWidget(self.hideFormButton)
        #self.verticalLayout.addLayout(self.horizontalLayout_3)
        #self.hideFormButton.clicked.connect(self.hideButtonClicked)
        
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
        #self.cancelEditButton.setVisible(self.current_id != None)
        self.horizontalLayout_5.addWidget(self.cancelEditButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        
        # connect buttons
        self.cancelEditButton.clicked.connect(self.cancelButtonClicked)
        self.addProjectButton.clicked.connect(self.addButtonClicked)
        
        # Settings
        self.settings = QtCore.QSettings("tracks-queue", "tracks-queue")
        
        # Add a vertical spacer
        spacerItem = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
        # Set up keyboard shortcuts
        shortcut = QtGui.QShortcut(self)
        shortcut.setKey(QtGui.QKeySequence("Esc"))
        shortcut.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        shortcut.activated.connect(self.cancelButtonClicked)
        
    #def hideButtonClicked(self):
    #    logging.info("TracksContextEditor->hideButtonClicked")
    #    self.formVisible = not self.formVisible
    #    self.settings.setValue("editor/visible", QtCore.QVariant(self.formVisible))
    #    self.updateHidden()
        
    #def updateHidden(self):
    #    logging.info("TracksContextEditor->setHidden")
    #            
    #    if self.formVisible:
    #        self.hideFormButton.setText(">> Hide Form")
    #        self.setMaximumSize(QtCore.QSize(250, 16777215))
    #        self.setMinimumSize(QtCore.QSize(250, 0))
    #        self.verticalLayout.setMargin(4)
    #        self.nameEdit.setFocus()
    #    else:
    #        self.hideFormButton.setText("<<")
    #        self.setMaximumSize(QtCore.QSize(30, 16777215))
    #        self.setMinimumSize(QtCore.QSize(30, 0))
    #        self.verticalLayout.setMargin(0)
    #    
    #    self.nameLabel.setVisible(self.formVisible)
    #    self.nameEdit.setVisible(self.formVisible)
    #    self.statusLabel.setVisible(self.formVisible)
    #    self.statusRadio1.setVisible(self.formVisible)
    #    self.statusRadio2.setVisible(self.formVisible)
    #    self.addProjectButton.setVisible(self.formVisible)
    #    #TODO only reshow cancel button when editing existing item
    #    self.cancelEditButton.setVisible(self.formVisible and self.current_id != None)
    
    def cancelButtonClicked(self):
        logging.info("TracksContextEditor->cancelButtonClicked")
        # Clear all the widgets
        # TODO also clear internal data reflecting the database item we are editing
        self.nameEdit.clear()
        self.statusRadio1.setChecked(True)
        
        self.current_id = None
        #self.cancelEditButton.setVisible(False)
        self.setVisible(False)
        self.addProjectButton.setText("Add context")

    def addButtonClicked(self):
        logging.info("TracksContextEditor->addButtonClicked")
        # Need to either save an existing context, or add a new context
        if (self.nameEdit.text()=="") or (self.statusRadio1.isChecked()==self.statusRadio2.isChecked()):
            QtGui.QMessageBox.critical(self,
                            "Error",
                            "Context editor is either incomplete or erroneous\n\nNo data has been inserted or modified")
            return
        if self.current_user_id==None:
            QtGui.QMessageBox.critical(self,
                            "Error",
                            "Editor doesn't know which user?\n\nNo data has been inserted or modified")
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
            q = "INSERT INTO contexts VALUES(NULL,?,1,?,?,DATETIME('now'),DATETIME('now'))"
            self.databaseCon.execute(q,[name,hidden,self.current_user_id])
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
        self.setVisible(True)
        self.setFocus()
        
    def setCurrentUser(self, user):
        """Change the current database user"""
        self.current_user_id = user

    def setFocus(self):
        logging.info("TracksContextEditor->setFocus")
        self.nameEdit.setFocus()
                
    def refresh(self):
        """Refresh the data and display of the editor"""
        logging.info("TracksContextEditor->refresh")
        # What is the setting re form visibility?
        if self.settings.contains("editor/visible"):
            self.formVisible = bool(self.settings.value("editor/visible").toBool())
            self.updateHidden()
		
