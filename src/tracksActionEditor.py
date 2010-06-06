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
    
    def __init__(self, dbCon):
        logging.info("TracksActionEditor initiated...")
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
        #self.setTitle("Johnny")
        
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
        projectStringList = QtCore.QStringList(["john", "joe", "tony"])
        projectCompleter = QtGui.QCompleter(projectStringList)
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
        for row in self.databaseCon.execute("select name FROM contexts"):
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
        
        # Date fields
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.verticalLayout_1 = QtGui.QVBoxLayout()
        self.verticalLayout_1.setSpacing(0)
        self.dueLabel = QtGui.QLabel(self)
        self.dueLabel.setText("Due")
        self.verticalLayout_1.addWidget(self.dueLabel)
        self.dueEdit = QtGui.QDateEdit(QtCore.QDate.currentDate())
        self.dueEdit.setCalendarPopup(True)
        self.dueCheckBox = QtGui.QCheckBox()#TODO
        self.dueEdit.setDisabled(True)
        
        self.verticalLayout_1.addWidget(self.dueEdit)
        self.horizontalLayout_2.addWidget(self.dueCheckBox)
        self.horizontalLayout_2.addLayout(self.verticalLayout_1)
        
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.showFromLabel = QtGui.QLabel(self)
        self.showFromLabel.setText("Show from")
        self.verticalLayout_2.addWidget(self.showFromLabel)
        self.showFromEdit = QtGui.QDateEdit(QtCore.QDate.currentDate())
        self.showFromEdit.setCalendarPopup(True)
        self.showFromCheckBox = QtGui.QCheckBox()#TODO
        self.showFromEdit.setDisabled(True)
        
        self.verticalLayout_2.addWidget(self.showFromEdit)
        self.horizontalLayout_2.addWidget(self.showFromCheckBox)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        
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
        self.tagsLabel.setVisible(self.formVisible)
        self.tagsEdit.setVisible(self.formVisible)
        self.dueLabel.setVisible(self.formVisible)
        self.dueEdit.setVisible(self.formVisible)
        self.showFromLabel.setVisible(self.formVisible)
        self.showFromEdit.setVisible(self.formVisible)
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
    
    def cancelButtonClicked(self):
        logging.info("TracksActionEditor->cancelButtonClicked")
        # Clear all the widgets
        # TODO also clear internal data reflecting the database item we are editing
        self.descriptionEdit.clear()
        self.notesEdit.clear()
        self.projectEdit.clear()
        self.contextEdit.clear()
        self.tagsEdit.clear()
        self.dueEdit.clear()
        self.showFromEdit.clear()
        
        self.current_id = None
        self.cancelEditButton.setVisible(False)
        self.addActionButton.setText("Add Action")
        
    def addActionButtonClicked(self):
        """Add a new action to db, or modify an existing one"""
        logging.info("TracksActionEditor->addActionButtonClicked")
        
        if self.descriptionEdit.text() == "" or self.contextEdit.text()== "":
            QtGui.QMessageBox.critical(self,
                            "Error",
                            "An action must have a description\n\nNo data has been inserted or modified")
            return
        if self.current_id == None:
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
            
            q = "insert into todos values(NULL,?,?,?,?,DATETIME('now'),NULL,NULL,1,NULL,'active',NULL,DATETIME('now'))"
            self.databaseCon.execute(q,[context,project,desc,notes])
            self.databaseCon.commit()

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
                self.dueEdit.setText(row[2])
            else:
                self.dueEdit.clear()
            if row[3]:
                self.showFromEdit.setText(row[3])
            else:
                self.showFromEdit.clear()
                
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