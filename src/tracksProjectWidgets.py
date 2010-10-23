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

class TracksProjectList(QtGui.QWidget):
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
        self.listWidget.setVisible(not self.listWidget.isVisible())
    
    
    def fillList(self):
        """Fill the list widget"""
        logging.info("TracksProjectList->fillList")
        if not self.dbQuery:
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
            horizontalLayout.setContentsMargins(-1, 2, -1, 0)
            horizontalLayout.setSpacing(0)
            
            # Delete Button
            deleteButton = QtGui.QToolButton(widget)
            deleteButton.setStyleSheet("border: None;")
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
            editButton = QtGui.QToolButton(widget)
            editButton.setStyleSheet("Border: none;")
            editIcon = None
            if QtGui.QIcon.hasThemeIcon("accessories-text-editor"):
                editIcon = QtGui.QIcon.fromTheme("accessories-text-editor")
            else:
                editIcon = QtGui.QIcon(self.iconPath + "accessories-text-editor.png")
            editButton.setIcon(editIcon)
            horizontalLayout.addWidget(editButton)
            self.projectEditButtonMapper.setMapping(editButton, projectID)
            editButton.clicked.connect(self.projectEditButtonMapper.map)
            
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
        
        self.listWidget.setFixedHeight(count*28+6)  
    
    
    def deleteProjectButtonClicked(self, id):
        logging.info("TracksProjectList->deleteContextButtonClicked  -  " + str(id))
        reallydelete = QtGui.QMessageBox.question(self, "tracks.cute: Really Delete?", "Are you sure you want to delete this project and clear the project field of all related actions?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        logging.debug("TracksContextList->deleteContextButtonClicked, reallydelete=" + str(reallydelete==QtGui.QMessageBox.Yes))
        
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
        self.refresh()

class TracksProjectEditor(QtGui.QGroupBox):
    """
    Provides an editor for GTD projects
    """
    # TODO define signals emitted by this widget
    __pyqtSignals__ = ("projectMoodified()",
                     )
    projectModified = QtCore.pyqtSignal()

    def __init__(self, dbCon):
        logging.info("TracksProjectEditor initiated...")
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
        self.formVisible = True
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.hideFormButton = QtGui.QPushButton(self)
        self.hideFormButton.setText(">> Hide Form")
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
        
        # Description edit
        self.descriptionLabel = QtGui.QLabel(self)
        self.descriptionLabel.setText("Description")
        self.verticalLayout.addWidget(self.descriptionLabel)
        self.descriptionEdit = QtGui.QPlainTextEdit(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.descriptionEdit.sizePolicy().hasHeightForWidth())
        self.descriptionEdit.setSizePolicy(sizePolicy)
        self.descriptionEdit.setMinimumSize(QtCore.QSize(0, 120))
        self.descriptionEdit.setMaximumSize(QtCore.QSize(16777215, 120))
        self.verticalLayout.addWidget(self.descriptionEdit)
        
        
        # Default context Line Edit
        self.contextLabel = QtGui.QLabel(self)
        self.contextLabel.setText("Default Context (Optional)")
        self.verticalLayout.addWidget(self.contextLabel)
        self.contextEdit = QtGui.QLineEdit(self)
        self.verticalLayout.addWidget(self.contextEdit)
        # Add string list completer
        # TODO get projects from database
        contextList = []
        for row in self.databaseCon.execute("select name FROM contexts"):
            contextList.append(row[0])
        contextStringList = QtCore.QStringList(contextList)
        contextCompleter = QtGui.QCompleter(contextStringList)
        contextCompleter.setCompletionMode(1)
        self.contextEdit.setCompleter(contextCompleter)

        
        # Default Tags Line Edit
        # TODO find existing tags from database
        self.existingTags = ["one", "two", "three", "four"]
        #
        self.tagsLabel = QtGui.QLabel(self)
        self.tagsLabel.setText("Default Tags (Optional)")
        self.verticalLayout.addWidget(self.tagsLabel)
        self.tagsEdit = QtGui.QLineEdit(self)
        self.verticalLayout.addWidget(self.tagsEdit)
        # TODO add completion. Consider this: http://john.nachtimwald.com/2009/07/04/qcompleter-and-comma-separated-tags/
        # make tags all lower case
        # use set(list of strings) and set.diffence
        #QObject.connect(self, SIGNAL('textChanged(QString)'), self.text_changed)
        self.tagsEdit.textChanged.connect(self.tagsEditChanged)
        self.tagCompleter = QtGui.QCompleter(QtCore.QStringList(self.existingTags))
        self.tagCompleter.setWidget(self.tagsEdit)
        self.tagCompleter.setCompletionMode(1)
        self.tagCompleter.activated.connect(self.tagsCompleterSelect)
        
        
        # Project state
        self.statusLabel = QtGui.QLabel(self)
        self.statusLabel.setText("Project Status")
        self.verticalLayout.addWidget(self.statusLabel)
        
        self.statusLayout = QtGui.QHBoxLayout()
        self.statusRadio1 = QtGui.QRadioButton(self)
        self.statusRadio1.setText("active")
        self.statusRadio1.setChecked(True)
        self.statusLayout.addWidget(self.statusRadio1)
        self.statusRadio2 = QtGui.QRadioButton(self)
        self.statusRadio2.setText("hidden")
        self.statusLayout.addWidget(self.statusRadio2)
        self.statusRadio3 = QtGui.QRadioButton(self)
        self.statusRadio3.setText("completed")
        self.statusLayout.addWidget(self.statusRadio3)
        self.verticalLayout.addLayout(self.statusLayout)
        
        
        # Commit and Cancel button
        # TODO hide cancel button by default??? only show when editing an existing item
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.addProjectButton = QtGui.QPushButton(self)
        self.addProjectButton.setText("Add project")
        self.horizontalLayout_5.addWidget(self.addProjectButton)
        self.cancelEditButton = QtGui.QPushButton(self)
        self.cancelEditButton.setText("Cancel edit")
        self.horizontalLayout_5.addWidget(self.cancelEditButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        # connect buttons
        self.addProjectButton.clicked.connect(self.saveButtonClicked)
        self.cancelEditButton.clicked.connect(self.cancelButtonClicked)
        
        self.cancelEditButton.setVisible(self.current_id != None)
        
        # Settings
        self.settings = QtCore.QSettings("tracks.cute", "tracks.cute")
        
        
    def hideButtonClicked(self):
        logging.info("TracksProjectEditor->hideButtonClicked")
        self.formVisible = not self.formVisible
        self.settings.setValue("editor/visible", QtCore.QVariant(self.formVisible))
        self.updateHidden()
        
    def updateHidden(self):
        logging.info("TracksProjectEditor->updateHidden")
        if self.formVisible:
            self.hideFormButton.setText(">> Hide Form")
            self.setMaximumSize(QtCore.QSize(250, 16777215))
            self.setMinimumSize(QtCore.QSize(250, 0))
            self.verticalLayout.setMargin(4)
        else:
            self.hideFormButton.setText("<<")
            self.setMaximumSize(QtCore.QSize(30, 16777215))
            self.setMinimumSize(QtCore.QSize(30, 0))
            self.verticalLayout.setMargin(0)
        
        # Hide or show all of the form elements
        self.descriptionLabel.setVisible(self.formVisible)
        self.descriptionEdit.setVisible(self.formVisible)
        self.nameLabel.setVisible(self.formVisible)
        self.nameEdit.setVisible(self.formVisible)
        self.contextLabel.setVisible(self.formVisible)
        self.contextEdit.setVisible(self.formVisible)
        self.tagsLabel.setVisible(False)#self.formVisible) TODO
        self.tagsEdit.setVisible(False)#self.formVisible) TODO
        self.statusLabel.setVisible(self.formVisible)
        self.statusRadio1.setVisible(self.formVisible)
        self.statusRadio2.setVisible(self.formVisible)
        self.statusRadio3.setVisible(self.formVisible)
        self.addProjectButton.setVisible(self.formVisible)
        #TODO only reshow cancel button when editing existing item
        self.cancelEditButton.setVisible(self.formVisible and self.current_id != None)
        
    def tagsEditChanged(self, theText):
        # refer to this example:
        # http://john.nachtimwald.com/2009/07/04/qcompleter-and-comma-separated-tags/
        #logging.info("TracksActionEditor->tagsEditChanged  -  "+str(theText))
        
        tagText = str(theText).lower().split(",")
        theTags = []
        for tag in tagText:
            tag = tag.strip()
            if len(tag) > 0:
                theTags.append(tag)
        theSet = list(set(theTags))
        
        currentText = str(theText[:self.tagsEdit.cursorPosition()])
        prefix = currentText.split(',')[-1].strip()

        tags =  list(set(self.existingTags).difference(theSet))
        model = QtGui.QStringListModel(QtCore.QStringList(tags), self.tagCompleter)
        model.sort(0)
        self.tagCompleter.setModel(model)
        self.tagCompleter.setCompletionPrefix(prefix)
        if prefix.strip() != '':
            self.tagCompleter.complete()
        self.tagCompleter.setModelSorting(2)
        
    def tagsCompleterSelect(self, theText):
        # refer to this example:
        # http://john.nachtimwald.com/2009/07/04/qcompleter-and-comma-separated-tags/
        #logging.info("TracksActionEditor->tagsCompleterSelect  -  " + str(theText))
        
        cursor_pos = self.tagsEdit.cursorPosition()
        before_text = unicode(self.tagsEdit.text())[:cursor_pos]
        after_text = unicode(self.tagsEdit.text())[cursor_pos:]
        prefix_len = len(before_text.split(',')[-1].strip())
        self.tagsEdit.setText('%s%s, %s' % (before_text[:cursor_pos - prefix_len], theText, after_text))
        self.tagsEdit.setCursorPosition(cursor_pos - prefix_len + len(theText) + 2)
    
    def cancelButtonClicked(self):
        logging.info("TracksProjectEditor->cancelButtonClicked")
        # Clear all the widgets
        # TODO also clear internal data reflecting the database item we are editing
        self.descriptionEdit.clear()
        self.nameEdit.clear()
        self.contextEdit.clear()
        self.tagsEdit.clear()
        self.statusRadio1.setChecked(True)
        
        self.current_id = None
        self.cancelEditButton.setVisible(False)
        self.addProjectButton.setText("Add Project")
        
    def saveButtonClicked(self):
        logging.info("TracksProjectEditor->saveButtonClicked")
        
        if self.nameEdit.text()=="":
            QtGui.QMessageBox.critical(self,
                            "Error",
                            "Project editor is either incomplete or erroneous\n\nNo data has been inserted or modified")
            return
        if self.current_user_id==None:
            QtGui.QMessageBox.critical(self,
                            "Error",
                            "Editor doesn't know which user??\n\nNo data has been inserted or modified")
            return
        
        name = str(self.nameEdit.text())
        desc = str(self.descriptionEdit.toPlainText())
        context = str(self.contextEdit.text())
        if context == "":
            context= None
        else:
            # look up the id in the database, error if it does not exist.
            result = self.databaseCon.execute("select id FROM contexts where name=?", [context,]).fetchone()
            if result != None:
                context = result[0]
            else:
                QtGui.QMessageBox.critical(self,
                            "Error",
                            "Nominated context doesn't exist (should prompt to add it in the future)\n\nNo data has been inserted or modified")
                return
        tags = None
        state = "active"
        if self.statusRadio1.isChecked():
            state = "active"
        elif self.statusRadio2.isChecked():
            state = "hidden"
        elif self.statusRadio3.isChecked():
            state = "completed"
        
    
                #TODO more here            
        if self.current_id == None:
            logging.debug("TracksProjectEditor->saveButtonClicked->adding new project")
            q = "INSERT INTO projects VALUES(NULL,?,1,?,?,?,DATETIME('now'),DATETIME('now'),?,NULL,?)"
            if state == "completed":
                q = "INSERT INTO projects VALUES(NULL,?,1,?,?,?,DATETIME('now'),DATETIME('now'),?,DATETIME('now'),?)"
            self.databaseCon.execute(q,[name,self.current_user_id,desc,state,context,tags])
            self.databaseCon.commit()
            
            self.cancelButtonClicked()
            
            self.emit(QtCore.SIGNAL("projectModified()"))
            
            
        else:
            logging.debug("TracksProjectEditor->saveButtonClicked->modifying existing project")
            
            q = "UPDATE projects SET name=?, description=?, state=?, default_context_id=?, default_tags=?, updated_at=DATETIME('now') WHERE id=?"
            if state == "completed" and state != self.current_id_prevstatus:
                q = "UPDATE projects SET name=?, description=?, state=?, default_context_id=?, default_tags=?, updated_at=DATETIME('now'), completed_at=DATETIME('now') WHERE id=?"
            self.databaseCon.execute(q,[name,desc,state,context,tags,self.current_id])
            self.databaseCon.commit()
            
            self.cancelButtonClicked()
            
            self.emit(QtCore.SIGNAL("projectModified()"))
            

    def setCurrentProjectID(self, projectID):
        logging.info("TracksProjectEditor->setCurrentProjectID")

        for row in self.databaseCon.execute("select id, name, description, state, default_context_id, default_tags FROM projects where id="+str(projectID)):
            self.nameEdit.setText(row[1])
            self.descriptionEdit.setPlainText(row[2])
            #context
            if row[4] != None:
                for name in self.databaseCon.execute("select name from contexts where id =?",[str(row[4]),]):
                    self.contextEdit.setText(name[0])
            #tags
            if row[5] != None:
                self.tagsEdit.setText(row[5])
            # the state
            if row[3] == "active":
                self.statusRadio1.setChecked(True)
                self.current_id_prevstatus = "active"
            elif row[3] == "hidden":
                self.statusRadio2.setChecked(True)
                self.current_id_prevstatus = "hidden"
            elif row[3] == "completed":
                self.statusRadio3.setChecked(True)
                self.current_id_prevstatus = "completed"
            else:
                self.statusRadio1.setChecked(True)
                self.current_id_prevstatus = "active"
        
        self.current_id=projectID
        self.addProjectButton.setText("Save project")
        self.cancelEditButton.setVisible(True)
        ## Make the editor visible if not already
        if not self.formVisible:
            self.hideButtonClicked()
        
    def setCurrentUser(self, user):
        """Change the current database user"""
        self.current_user_id = user
        
    def refresh(self):
        logging.info("TracksProjectEditor->refresh")
        # What is the setting re form visibility?
        if self.settings.contains("editor/visible"):
            self.formVisible = bool(self.settings.value("editor/visible").toBool())
            self.updateHidden()
            
        # update the context auto complete list
        contextList = []
        for row in self.databaseCon.execute("SELECT name FROM contexts WHERE user_id=? ORDER BY UPPER(name)", (self.current_user_id,)):
            contextList.append(row[0])
        contextStringList = QtCore.QStringList(contextList)
        contextCompleter = QtGui.QCompleter(contextStringList)
        contextCompleter.setCompletionMode(1)
        self.contextEdit.setCompleter(contextCompleter) 