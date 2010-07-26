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
                     "gotoLabel(QString)",
                     "gotoProject(int)",
                     "actionModified()"
                     )
    editAction = QtCore.pyqtSignal(int)
    starAction = QtCore.pyqtSignal(int)
    deleteAction = QtCore.pyqtSignal(int)
    completeAction = QtCore.pyqtSignal(int)
    gotoLabel = QtCore.pyqtSignal(QtCore.QString)
    gotoProject = QtCore.pyqtSignal(int)
    actionModified = QtCore.pyqtSignal()

    # Need to add a list title, a database query, an option for expanded or not
    def __init__(self, databaseCon, title, dbQuery, startExpanded):
        logging.info("TracksActionList initiated...")
        self.databaseCon = databaseCon
        self.dbQuery = dbQuery
        
        QtGui.QWidget.__init__(self)
        
        # Options with defaults
        self.displayshow_from = False
        self.displaycompleted_at = False
        self.displaytags = False
        self.displayprojectfirst = False
        
        
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
        
        self.itemCompleteButtonMapper = QtCore.QSignalMapper(self)
        self.itemCompleteButtonMapper.mapped[int].connect(self.completeItemButtonClicked)
        
        self.itemLabelButtonMapper = QtCore.QSignalMapper(self)
        self.itemLabelButtonMapper.mapped[int].connect(self.labelItemButtonClicked)
        
        self.itemProjectButtonMapper = QtCore.QSignalMapper(self)
        self.itemProjectButtonMapper.mapped[int].connect(self.projectItemButtonClicked)
        
        
        # Add items to the list, removed, call refresh() to actually fill list.
        #self.fillList()
        
        # Resize items in the list and then resize the list.
        #h = 0
        #for a in range(self.listWidget.count()):
        #   i = self.listWidget.item(a)
        #   i.setSizeHint(QtCore.QSize(0,22))
        #   h += self.listWidget.sizeHintForRow(a)
        #self.listWidget.setFixedHeight(h+6)
    
    def setDisplayProjectFirst(self, setto):
        self.displayprojectfirst = setto
        
    def setDisplayShowFrom(self, setto):
        logging.info("TracksActionList->setDisplayShowFrom")
        self.displayshow_from = setto
        
    def setDisplayCompletedAt(self, setto):
        logging.info("TracksActionList->setDisplayCompletedAt")
        self.displaycompleted_at = setto
    
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
    # action id, action description, state, context_id, context_name, project_id, project_name
    def fillList(self):
        """Fill the list widget"""
        logging.info("TracksActionList->fillList")
        numberOfItems = 6
        
        count = 0
        if self.dbQuery == None:
            self.dbQuery = "select id, description, 0, 0, 0, 0, 0 from todos order by description"
        for row in self.databaseCon.execute(self.dbQuery):
            id = row[0]
            desc = row[1]
            context = row[4]
            if context == 0:
                context = None
            project_id = row[5]
            project = row[6]
            if project == 0:
                project = None
            state = row[2]

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
            if state == "completed":
                checkBox.setChecked(True)
            #checkBox.setMaximumSize(QtCore.QSize(12,12)) #TEST
            horizontalLayout.addWidget(checkBox)
            self.itemCompleteButtonMapper.setMapping(checkBox, id)
            checkBox.stateChanged.connect(self.itemCompleteButtonMapper.map)
            #TODO make this do something
            
            # Completed_At date if required
            is_completed = False
            if self.displaycompleted_at:
                date = self.databaseCon.execute("select datetime(completed_at, 'localtime') from todos where id = " + str(id)).fetchone()[0]
                if date:
                    is_completed = True
                    completed_atText = QtGui.QLabel(widget)
                    completed_atText.setText("[" + str(date) +"]")
                    completed_atText.setStyleSheet("Font-size: 8px")
                    horizontalLayout.addWidget(completed_atText)
            
            # Show_from date if required
            if self.displayshow_from:
                show_fromText = QtGui.QLabel(widget)
                date = self.databaseCon.execute("select show_from from todos where id = " + str(id)).fetchone()[0]
                show_fromText.setText("[" + str(date) +"]")
                show_fromText.setStyleSheet("Font-size: 8px")
                horizontalLayout.addWidget(show_fromText)
             
            # Project first if required
            if self.displayprojectfirst:
                projecttext = QtGui.QLabel(widget)
                #projecttext.setText(" %-30s  \t" % str(project)[0:30])
                projecttext.setText(project)
                projecttext.setStyleSheet("Font-size: 8px")
                projecttext.setMinimumWidth(140)
                projecttext.setMaximumWidth(140)
                horizontalLayout.addWidget(projecttext)
                
            # Due date if required
            data = self.databaseCon.execute("select due, (due < DATE('now','localtime')) from todos where id = " + str(id)).fetchone()
            if is_completed:
                data = self.databaseCon.execute("select due, (due < DATE(completed_at,'localtime')) from todos where id = " + str(id)).fetchone()
            date = data[0]
            overdue = bool(data[1])
            if date: #
                dueText = QtGui.QLabel(widget)
                dueText.setText("!" + str(date) +"!")
                dueText.setFixedHeight(10)
                if overdue:
                    dueText.setStyleSheet("Font-size: 8px; color: white; Background-color: 'orangered'")
                else:
                    dueText.setStyleSheet("Font-size: 8px; color: black; Background-color: 'aliceblue'")
    
                horizontalLayout.addWidget(dueText)
            
            # Action Text
            actionText = QtGui.QLabel(widget)
            actionText.setText(desc)
            horizontalLayout.addWidget(actionText)
            
            # Label Button
            if self.displaytags:
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
                self.itemProjectButtonMapper.setMapping(projectButton, project_id) #TODO fix
                projectButton.clicked.connect(self.itemProjectButtonMapper.map)
            
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
        reallydelete = QtGui.QMessageBox.question(self, "tracks.cute: Really Delete", "Are you sure you want to delete this action?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        logging.debug("TracksActionList->deleteItemButtonClicked, reallydelete=" + str(reallydelete==QtGui.QMessageBox.Yes))
        
        
        
    def editItemButtonClicked(self, id):
        logging.info("TracksActionList->editItemButtonClicked  -  " + str(id))
        self.emit(QtCore.SIGNAL("editAction(int)"),id)

        
    def starItemButtonClicked(self, id):
        logging.info("TracksActionList->starItemButtonClicked  -  " + str(id))
        
    def completeItemButtonClicked(self, id):
        logging.info("TracksActionList->completeItemButtonClicked - " + str(id))
        
        current_state = self.databaseCon.execute("SELECT state FROM todos where id = ?", [id,]).fetchone()[0]
        if current_state == "completed":
            q = "UPDATE todos SET state=?, completed_at=NULL, updated_at=DATETIME('now') where id=?"
            self.databaseCon.execute(q,['active',id])
            self.databaseCon.commit()
        else:
            q = "UPDATE todos SET state=?, completed_at=DATETIME('now'), updated_at=DATETIME('now') where id=?"
            self.databaseCon.execute(q,['completed',id])
            self.databaseCon.commit()
        
        self.emit(QtCore.SIGNAL("completeAction(int)"),id)
        self.emit(QtCore.SIGNAL("actionModified()"))
        
    def labelItemButtonClicked(self, id):
        logging.info("TracksActionList->labelItemButtonClicked  -  " +str(id))
        
    def projectItemButtonClicked(self, id):
        logging.info("TracksActionList->projectItemButtonClicked  -  " +str(id))
        self.emit(QtCore.SIGNAL("gotoProject(int)"), id)
        
    def refresh(self):
        logging.info("TracksActionList->refresh")
        self.listWidget.clear()
        self.fillList()
        
    def setDBQuery(self, dbQuery):
        logging.info("TracksActionList->setDBQuery")
        self.dbQuery = dbQuery
        self.refresh()
        
class DumbWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
    def mousePressEvent(self, event):
        print "clicked"