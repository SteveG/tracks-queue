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
#NOTE PyQt4.QtCore.QDateTime.currentDateTime().toUTC().toLocalTime()
#>>> foo = PyQt4.QtCore.QDateTime.fromString("2010-05-27 11:52:14", "yyyy-MM-dd HH:mm:ss")
#>>> foo.setTimeSpec(1)
#>>> foo.toLocalTime()
#PyQt4.QtCore.QDateTime(2010, 5, 27, 21, 22, 14)
"""
Provides an editor side pane for GTD actions
"""

from PyQt4 import QtCore, QtGui
import logging

class TracksActionEditor(QtGui.QGroupBox):
    """Provides a sidebar widget for editing/creating actions"""
    # TODO define signals emitted by this widget
    __pyqtSignals__ = ("actionModified()"
                     )
    actionModified = QtCore.pyqtSignal()
    
    def __init__(self, dbCon):
        logging.info("TracksActionEditor initiated...")
        # The current item id
        self.current_id = None
        
        self.databaseCon = dbCon
        self.current_user_id = None
        
        # default values
        self.defaultContext = None
        self.defaultProject = None
        self.defaultTags = None
        
        
        QtGui.QGroupBox.__init__(self)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QtCore.QSize(250, 16777215))
        self.setMinimumSize(QtCore.QSize(250, 0))
        #self.setTitle("Johnny")
        
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        
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
        
        # Description line edit
        self.descriptionLabel = QtGui.QLabel(self)
        self.descriptionLabel.setText("Description")
        self.verticalLayout.addWidget(self.descriptionLabel)
        self.descriptionEdit = QtGui.QLineEdit(self)
        self.verticalLayout.addWidget(self.descriptionEdit)
        
        # Notes edit
        self.notesLabel = QtGui.QLabel(self)
        self.notesLabel.setText("Notes")
        self.verticalLayout.addWidget(self.notesLabel)
        self.notesEdit = QtGui.QPlainTextEdit(self)
        self.notesEdit.setTabChangesFocus(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.notesEdit.sizePolicy().hasHeightForWidth())
        self.notesEdit.setSizePolicy(sizePolicy)
        self.notesEdit.setMinimumSize(QtCore.QSize(0, 120))
        self.notesEdit.setMaximumSize(QtCore.QSize(16777215, 120))
        self.verticalLayout.addWidget(self.notesEdit)
        
        # Project Line Edit
        self.projectLabel = QtGui.QLabel(self)
        self.projectLabel.setText("Project")
        self.verticalLayout.addWidget(self.projectLabel)
        self.projectEdit = QtGui.QLineEdit(self)
        self.verticalLayout.addWidget(self.projectEdit)
        # Add string list completer
        # TODO get projects from database
        projectList = []
        for row in self.databaseCon.execute("select name FROM projects ORDER BY name"):
            projectList.append(row[0])
        projectCompleter = QtGui.QCompleter(projectList)
        projectCompleter.setCompletionMode(1)
        self.projectEdit.setCompleter(projectCompleter)
        
        # Context Line Edit
        self.contextLabel = QtGui.QLabel(self)
        self.contextLabel.setText("Context")
        self.verticalLayout.addWidget(self.contextLabel)
        self.contextEdit = QtGui.QLineEdit(self)
        self.verticalLayout.addWidget(self.contextEdit)
        # Add string list completer
        # TODO get contexts from database
        contextList = []
        for row in self.databaseCon.execute("select name FROM contexts ORDER BY name"):
            contextList.append(row[0])
        contextStringList = QtCore.QStringList(contextList)
        contextCompleter = QtGui.QCompleter(contextStringList)
        contextCompleter.setCompletionMode(1) # This displays all possible options, but pressing
        # down goes to the best match
        self.contextEdit.setCompleter(contextCompleter)
        
        # Tags Line Edit
        # TODO find existing tags from database
        self.existingTags = []
        for row in self.databaseCon.execute("select name FROM tags"):
            self.existingTags.append(row[0])
        self.existingTags.append("FAKE-TAG")
        #
        self.tagsLabel = QtGui.QLabel(self)
        self.tagsLabel.setText("Tags (Separate with commas)")
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
        # make tags invisible
        self.tagsLabel.setVisible(False)
        self.tagsEdit.setVisible(False)
        
        # Date fields
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.verticalLayout_1 = QtGui.QVBoxLayout()
        self.verticalLayout_1.setSpacing(0)
        self.dueEdit = QtGui.QDateEdit(QtCore.QDate.currentDate())
        self.dueEdit.setCalendarPopup(True)
        self.dueCheckBox = QtGui.QCheckBox()
        self.dueCheckBox.setText("Due")
        self.dueCheckBox.stateChanged.connect(self.dueDateCheckChanged)
        self.dueEdit.setDisabled(True)
        
        self.verticalLayout_1.addWidget(self.dueCheckBox)
        self.verticalLayout_1.addWidget(self.dueEdit)
        self.horizontalLayout_2.addLayout(self.verticalLayout_1)
        
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.showFromEdit = QtGui.QDateEdit(QtCore.QDate.currentDate())
        self.showFromEdit.setCalendarPopup(True)
        self.showFromCheckBox = QtGui.QCheckBox()
        self.showFromCheckBox.setText("Show from")
        self.showFromCheckBox.stateChanged.connect(self.showFromCheckChanged)
        self.showFromEdit.setDisabled(True)
        
        self.verticalLayout_2.addWidget(self.showFromCheckBox)
        self.verticalLayout_2.addWidget(self.showFromEdit)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        
        # Depends on
        self.existingActions = []
        for row in self.databaseCon.execute("select description FROM todos where state='active'"):
            self.existingActions.append(row[0])
        #self.existingActions.append("FAKE-TAG")
        #
        self.dependsLabel = QtGui.QLabel(self)
        self.dependsLabel.setText("Depends on (Separate with ;)")
        self.verticalLayout.addWidget(self.dependsLabel)
        self.dependsEdit = QtGui.QLineEdit(self)
        self.verticalLayout.addWidget(self.dependsEdit)
        # TODO add completion. Consider this: http://john.nachtimwald.com/2009/07/04/qcompleter-and-comma-separated-tags/
        # make tags all lower case
        # use set(list of strings) and set.diffence
        self.dependsEdit.textChanged.connect(self.dependsEditChanged)
        self.dependsCompleter = QtGui.QCompleter(QtCore.QStringList(self.existingActions))
        self.dependsCompleter.setWidget(self.dependsEdit)
        self.dependsCompleter.setCompletionMode(1)
        self.dependsCompleter.activated.connect(self.dependsCompleterSelect)
        
        # Commit and Cancel button
        # TODO hide cancel button by default??? only show when editing an existing item
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.addActionButton = QtGui.QPushButton(self)
        self.addActionButton.setText("Add action")
        self.horizontalLayout_5.addWidget(self.addActionButton)
        self.cancelEditButton = QtGui.QPushButton(self)
        self.cancelEditButton.setText("Cancel edit")
        self.horizontalLayout_5.addWidget(self.cancelEditButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        # connect buttons
        self.cancelEditButton.clicked.connect(self.cancelButtonClicked)
        self.addActionButton.clicked.connect(self.addActionButtonClicked)
        
        self.cancelEditButton.setVisible(self.current_id != None)
    
    def dueDateCheckChanged(self):
        """Check box enabling the due date has been clicked"""
        logging.info("TracksActionEditor->dueDateCheckChanged")
        self.dueEdit.setDisabled(not self.dueCheckBox.isChecked())
    
    def showFromCheckChanged(self):
        """Check box enabling the show from date has been clicked"""
        logging.info("TracksActionEditor->showFromCheckChanged")
        self.showFromEdit.setDisabled(not self.showFromCheckBox.isChecked())
        
    def hideButtonClicked(self):
        logging.info("TracksActionEditor->hideButtonClicked")
        self.formVisible = not self.formVisible
        if self.formVisible:
            self.hideFormButton.setText(">> Hide Form")
            self.setMaximumSize(QtCore.QSize(250, 16777215))
            self.setMinimumSize(QtCore.QSize(250, 0))
        else:
            self.hideFormButton.setText("<<")
            self.setMaximumSize(QtCore.QSize(50, 16777215))
            self.setMinimumSize(QtCore.QSize(50, 0))
        
        # Hide or show all of the form elements
        self.descriptionLabel.setVisible(self.formVisible)
        self.descriptionEdit.setVisible(self.formVisible)
        self.notesLabel.setVisible(self.formVisible)
        self.notesEdit.setVisible(self.formVisible)
        self.projectLabel.setVisible(self.formVisible)
        self.projectEdit.setVisible(self.formVisible)
        self.contextLabel.setVisible(self.formVisible)
        self.contextEdit.setVisible(self.formVisible)
        self.tagsLabel.setVisible(False)#self.formVisible)
        self.tagsEdit.setVisible(False)#self.formVisible)
        self.dueEdit.setVisible(self.formVisible)
        self.dueCheckBox.setVisible(self.formVisible)
        self.showFromEdit.setVisible(self.formVisible)
        self.showFromCheckBox.setVisible(self.formVisible)
        self.dependsLabel.setVisible(self.formVisible)
        self.dependsEdit.setVisible(self.formVisible)
        self.addActionButton.setVisible(self.formVisible)
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
    
    def dependsEditChanged(self, theText):
        # refer to this example:
        # http://john.nachtimwald.com/2009/07/04/qcompleter-and-comma-separated-tags/
        #logging.info("TracksActionEditor->tagsEditChanged  -  "+str(theText))
        
        tagText = str(theText).split(";")
        theTags = []
        for tag in tagText:
            tag = tag.strip()
            if len(tag) > 0:
                theTags.append(tag)
        theSet = list(set(theTags))
        
        currentText = str(theText[:self.dependsEdit.cursorPosition()])
        prefix = currentText.split(';')[-1].strip()

        tags =  list(set(self.existingActions).difference(theSet))
        model = QtGui.QStringListModel(QtCore.QStringList(tags), self.dependsCompleter)
        model.sort(0)
        self.dependsCompleter.setModel(model)
        self.dependsCompleter.setCompletionPrefix(prefix)
        if prefix.strip() != '':
            self.dependsCompleter.complete()
        self.dependsCompleter.setModelSorting(1)
        
    def dependsCompleterSelect(self, theText):
        # refer to this example:
        # http://john.nachtimwald.com/2009/07/04/qcompleter-and-comma-separated-tags/
        #logging.info("TracksActionEditor->tagsCompleterSelect  -  " + str(theText))
        
        cursor_pos = self.dependsEdit.cursorPosition()
        before_text = unicode(self.dependsEdit.text())[:cursor_pos]
        after_text = unicode(self.dependsEdit.text())[cursor_pos:]
        prefix_len = len(before_text.split(';')[-1].strip())
        self.dependsEdit.setText('%s%s; %s' % (before_text[:cursor_pos - prefix_len], theText, after_text))
        self.dependsEdit.setCursorPosition(cursor_pos - prefix_len + len(theText) + 2)
    
    def cancelButtonClicked(self):
        logging.info("TracksActionEditor->cancelButtonClicked")
        # Clear all the widgets
        # TODO also clear internal data reflecting the database item we are editing
        self.descriptionEdit.clear()
        self.notesEdit.clear()
        self.projectEdit.clear()
        if self.defaultProject:
            self.projectEdit.setText(self.defaultProject)
        self.contextEdit.clear()
        if self.defaultContext:
            self.contextEdit.setText(self.defaultContext)
        self.tagsEdit.clear()
        if self.defaultTags:
            self.tagsEdit.setText(self.defaultTags)
        self.dueEdit.setDate(QtCore.QDate.currentDate())
        self.dueEdit.setDisabled(True)
        self.dueCheckBox.setChecked(False)
        self.showFromEdit.setDate(QtCore.QDate.currentDate())
        self.showFromEdit.setDisabled(True)
        self.showFromCheckBox.setChecked(False)
        self.dependsEdit.clear()
        
        self.current_id = None
        self.cancelEditButton.setVisible(False)
        self.addActionButton.setText("Add Action")
        
    def addActionButtonClicked(self):
        """Add a new action to db, or modify an existing one"""
        logging.info("TracksActionEditor->addActionButtonClicked")
        
        if self.descriptionEdit.text() == "" or self.contextEdit.text()== "":
            QtGui.QMessageBox.critical(self,
                            "Error",
                            "An action must have a description and a context\n\nNo data has been inserted or modified")
            return
        if self.current_user_id==None:
            QtGui.QMessageBox.critical(self,
                            "Error",
                            "Editor doesn't know the user?\n\nNo data has been inserted or modified")
            return
        
        desc = str(self.descriptionEdit.text())
        notes = str(self.notesEdit.toPlainText())
        # Context
        context = None
        try:
            context = self.databaseCon.execute("select id from contexts where name=?",[str(self.contextEdit.text()),]).fetchall()[0][0]
        except:
            QtGui.QMessageBox.critical(self,
                        "Error",
                        "Context doesn't exist\n\nThis may provide an option to create the context in the future\n\nNothing added")
            return
        # Project
        project = None
        try:
            project = self.databaseCon.execute("select id from projects where name=?",[str(self.projectEdit.text()),]).fetchall()[0][0]
        except:
            QtGui.QMessageBox.critical(self,
                        "Error",
                        "Project doesn't exist\n\nThis may provide an option to create the context in the future\n\nNothing added")
            return
        # Due Date
        due = None
        if self.dueCheckBox.isChecked():
            due = str(self.dueEdit.date().toString("yyyy-MM-dd"))
        # Show from Date
        show = None
        if self.showFromCheckBox.isChecked():
            show = str(self.showFromEdit.date().toString("yyyy-MM-dd"))
            
        # Depends on
        tagText = str(self.dependsEdit.text()).split(";")
        theTags = []
        dependsIDs = []
        if tagText:
            for tag in tagText:
                tag = tag.strip()
                if len(tag) > 0:
                    theTags.append(tag)
        try:
            for tag in theTags:
                id = self.databaseCon.execute("select id from todos where description=?",[tag,]).fetchone()[0]
                dependsIDs.append(id)
        except:
            QtGui.QMessageBox.critical(self,
                        "Error",
                        "Action doesn't exist\n\nWhat does this depend on?\n\nNothing added")
            return
        
        # Insert the data
        if self.current_id == None:
            q = "insert into todos values(NULL,?,?,?,?,DATETIME('now'),?,NULL,?,?,'active',NULL,DATETIME('now'))"
            self.databaseCon.execute(q,[context,project,desc,notes,due,self.current_user_id,show])
            self.databaseCon.commit()
            
            if len(dependsIDs) > 0:
                currentID = self.databaseCon.execute("SELECT last_insert_rowid()").fetchone()[0]
                for id in dependsIDs:
                    logging.debug("TracksActionEditor->addActionButtonClicked - Inserting a dependancy")
                    q = "insert into dependencies values(NULL,?,?,'depends')"
                    self.databaseCon.execute(q,[currentID,id])
                    self.databaseCon.commit()
            
        else:
            q = "UPDATE todos SET context_id=?, project_id=?, description=?, notes=?, due=?, show_from=?, updated_at=DATETIME('now') where id=?"
            self.databaseCon.execute(q,[context,project,desc,notes,due,show,self.current_id])
            self.databaseCon.commit()
            
            if len(dependsIDs) > 0:
                # remove all the old dependancies
                self.databaseCon.execute("DELETE FROM dependencies WHERE successor_id=?", [self.current_id,])
                
                currentID = self.current_id
                for id in dependsIDs:
                    logging.debug("TracksActionEditor->addActionButtonClicked - Inserting a dependancy")
                    q = "insert into dependencies values(NULL,?,?,'depends')"
                    self.databaseCon.execute(q,[currentID,id])
                    self.databaseCon.commit()
            
        self.cancelButtonClicked()
        self.emit(QtCore.SIGNAL("actionModified()"))
        
    def setCurrentActionID(self, actionID):
        logging.info("TracksActionEditor->setCurrentActionID")
        self.addActionButton.setText("Save Action")
        self.current_id = actionID
        self.cancelEditButton.setVisible(True)
        # Make the editor visible if not already
        if not self.formVisible:
            self.hideButtonClicked()
        
        # The General stuff
        for row in self.databaseCon.execute("select description, notes, due, show_from from todos WHERE id="+str(actionID)):
            self.descriptionEdit.setText(row[0])
            if row[1]:
                self.notesEdit.setPlainText(row[1])
            else:
                self.notesEdit.clear()
            if row[2]:
                # row[2] will be string in format yyyy-MM-dd
                self.dueCheckBox.setChecked(True)
                self.dueEdit.setDisabled(False)
                self.dueEdit.setDate(QtCore.QDate.fromString(row[2][0:10],"yyyy-MM-dd"))
            else:
                self.dueEdit.clear()
                self.dueCheckBox.setChecked(False)
                self.dueEdit.setDisabled(True)
            if row[3]:
                # row[3] will be string in format yyyy-MM-dd
                self.showFromCheckBox.setChecked(True)
                self.showFromEdit.setDisabled(False)
                self.showFromEdit.setDate(QtCore.QDate.fromString(row[3][0:10],"yyyy-MM-dd"))
                logging.debug("TracksActionEditor->setCurrentActionID  - show_from=" +str(row[3][0:10]))
            else:
                self.showFromEdit.clear()
                self.showFromCheckBox.setChecked(False)
                self.showFromEdit.setDisabled(True)
                
        # The Project
        self.projectEdit.clear()
        for row in self.databaseCon.execute("select projects.name FROM todos, projects WHERE todos.project_id=projects.id and todos.id="+str(actionID)):
            self.projectEdit.setText(row[0])
        # The context
        self.contextEdit.clear()
        for row in self.databaseCon.execute("select contexts.name from todos, contexts where todos.context_id=contexts.id and todos.id="+str(actionID)):
            self.contextEdit.setText(row[0])
            
        # The tags
        tagText = ""    
        for row in self.databaseCon.execute("select tags.name from todos, taggings, tags where todos.id=taggings.taggable_id and tags.id=taggings.tag_id and todos.id="+str(actionID)):
            if tagText == "":
                tagText.append(row[0])
            else:
                tagText.append(row[0])
            #self.nameEdit.setText(row[1])
            #if row[2] == "f":
            #   self.statusRadio1.setChecked(True)
            #else:
            #   self.statusRadio2.setChecked(True)
        self.tagsEdit.setText(tagText)
        
        # The dependancies
        dependText = ""
        for row in self.databaseCon.execute("SELECT todos.description FROM dependencies, todos WHERE todos.id=dependencies.predecessor_id and dependencies.successor_id=?",[actionID,]):
            dependText = dependText + str(row[0]+"; ")
        self.dependsEdit.setText(dependText)    
        

    
    def refresh(self):
        """This will refresh the action editor, ie update available projects/contexts/tags"""
        logging.info("tracksActionEditor->refresh")
        
        # Update list of available projects
        projectList = []
        for row in self.databaseCon.execute("SELECT name FROM projects ORDER BY name"):
            projectList.append(row[0])
        projectCompleter = QtGui.QCompleter(projectList)
        projectCompleter.setCompletionMode(1)
        self.projectEdit.setCompleter(projectCompleter)
        
        # Update list of available contexts
        contextList = []
        for row in self.databaseCon.execute("SELECT name FROM contexts ORDER BY name"):
            contextList.append(row[0])
        contextStringList = QtCore.QStringList(contextList)
        contextCompleter = QtGui.QCompleter(contextStringList)
        contextCompleter.setCompletionMode(1)
        self.contextEdit.setCompleter(contextCompleter)
        
        # TODO refresh the list of available tags
    
    def setDefaultProject(self, projectName):
        self.defaultProject = projectName
        
    def setDefaultContext(self, contextName):
        self.defaultContext = contextName
        
    def setDefaultTags(self, tags):
        self.defaultTags = tags
        
    def setCurrentUser(self, user):
        self.current_user_id = user