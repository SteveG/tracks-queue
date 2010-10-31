#!/usr/bin/env python2
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
import sys


class TracksActionList(QtGui.QWidget):
    # TODO define signals emitted by this widget
    __pyqtSignals__ = ("editAction(int)",
                     "starAction(int)",
                     "deleteAction(int)",
                     "completeAction(int)",
                     "gotoLabel(QString)",
                     "gotoProject(int)",
                     "gotoContext(int)",
                     "actionModified()",
                     "getFocus()"
                     )
    editAction = QtCore.pyqtSignal(int)
    starAction = QtCore.pyqtSignal(int)
    deleteAction = QtCore.pyqtSignal(int)
    completeAction = QtCore.pyqtSignal(int)
    gotoLabel = QtCore.pyqtSignal(QtCore.QString)
    gotoProject = QtCore.pyqtSignal(int)
    gotoContext = QtCore.pyqtSignal(int)
    actionModified = QtCore.pyqtSignal()
    getFocus = QtCore.pyqtSignal()

    # Need to add a list title, a database query, an option for expanded or not
    def __init__(self, databaseCon, title, dbQuery, startExpanded):
        logging.info("TracksActionList initiated...")
        self.iconPath = str(sys.path[0])+"/icons/"
        
        self.databaseCon = databaseCon
        self.dbQuery = dbQuery
        
        QtGui.QWidget.__init__(self)
        
        # Options with defaults
        self.displayshow_from = False
        self.displaycompleted_at = False
        self.displaytags = False
        self.displayprojectfirst = False
        self.displaycontextfirst = False

        # Create Layout
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        
        # Create expander button
        self.toggleListButton = CustomButton()
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
        self.connect(self.toggleListButton, QtCore.SIGNAL("ctrlclicked()"), self.toggleListButtonCtrlClick)
        
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
        self.itemContextButtonMapper = QtCore.QSignalMapper(self)
        self.itemContextButtonMapper.mapped[int].connect(self.contextItemButtonClicked)
    
    def setDisplayProjectFirst(self, setto):
        self.displayprojectfirst = setto
        
    def setDisplayContextFirst(self, setto):
        self.displaycontextfirst = setto
        
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
        
        self.setExpanded(not self.isExpanded())
    
    def toggleListButtonCtrlClick(self):
        """Aim of this is to expand just this list and emit a signal to minimise all others on the screen"""
        logging.info("TracksActionList->toggleListButtonCtrlClick")
        
        # ensure this list is visible
        #if not self.listWidget.isVisible():
        #    self.setExpanded(True)
        # emit signal to parent widget
        self.emit(QtCore.SIGNAL("getFocus()"))
        
    
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
            context_id = row[3]
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
            deleteButton.setStyleSheet("border: None;")
            deleteIcon = None
            if QtGui.QIcon.hasThemeIcon("edit-delete"):
                deleteIcon = QtGui.QIcon.fromTheme("edit-delete")
            else:
                deleteIcon = QtGui.QIcon(self.iconPath + "edit-delete.png")
            deleteButton.setIcon(QtGui.QIcon(deleteIcon.pixmap(16,16,0,0)))
            #deleteButton.setMaximumSize(QtCore.QSize(16,16)) #TEST
            horizontalLayout.addWidget(deleteButton)
            self.itemDeleteButtonMapper.setMapping(deleteButton, id)
            deleteButton.clicked.connect(self.itemDeleteButtonMapper.map)
            
            # Edit Button
            editButton = QtGui.QToolButton(widget)
            editButton.setStyleSheet("Border: none;")
            editIcon = None
            if QtGui.QIcon.hasThemeIcon("accessories-text-editor"):
                editIcon = QtGui.QIcon.fromTheme("accessories-text-editor")
            else:
                editIcon = QtGui.QIcon(self.iconPath + "accessories-text-editor.png")
            editButton.setIcon(editIcon)
            #editButton.setMaximumSize(QtCore.QSize(25,25)) #TEST
            horizontalLayout.addWidget(editButton)
            self.itemEditButtonMapper.setMapping(editButton, id)
            editButton.clicked.connect(self.itemEditButtonMapper.map)
            
            # Star Button
            is_starred_query = "select todos.description, tags.name from todos, tags, taggings where todos.id=taggings.taggable_id and tags.id = taggings.tag_id and tags.name='starred' and todos.id=?"
            is_starred_data = self.databaseCon.execute(is_starred_query, (id,)).fetchall()
            is_starred = True
            if len(is_starred_data)==0:
                is_starred=False
            
            starButton = QtGui.QToolButton(widget)
            starButton.setStyleSheet("border: None;")
            importantIcon = QtGui.QIcon.fromTheme("emblem-important")
            importantIcon = None
            if QtGui.QIcon.hasThemeIcon("emblem-important"):
                importantIcon = QtGui.QIcon.fromTheme("emblem-important")
            else:
                importantIcon = QtGui.QIcon(self.iconPath + "emblem-important.png")
            if is_starred:
                starButton.setIcon(QtGui.QIcon(importantIcon.pixmap(16,16,0,1)))
            else:
                starButton.setIcon(QtGui.QIcon(importantIcon.pixmap(16,16,1,1)))
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
                    completed_atText.setText("[" + str(date)[0:10] +"]  ")
                    completed_atText.setStyleSheet("Font-size: 8px")
                    horizontalLayout.addWidget(completed_atText)
            
            # Show_from date if required
            if self.displayshow_from:
                date = self.databaseCon.execute("select show_from from todos where id = " + str(id)).fetchone()[0]
                if date:
                    show_fromText = QtGui.QLabel(widget)
                    show_fromText.setText("[" + str(date) +"]")
                    show_fromText.setStyleSheet("Font-size: 8px")
                    horizontalLayout.addWidget(show_fromText)
             
            # Project first if required
            if self.displayprojectfirst:
                projecttext = QtGui.QPushButton(widget)
                projecttext.setCursor(QtCore.Qt.PointingHandCursor)
                projecttext.setStyleSheet("border: None; Font-size: 8px; text-align:left")
                projecttext.setText(project)
                projecttext.setMinimumWidth(70)
                projecttext.setMaximumWidth(70)
                horizontalLayout.addWidget(projecttext)
                self.itemProjectButtonMapper.setMapping(projecttext, project_id)
                projecttext.clicked.connect(self.itemProjectButtonMapper.map)
                
            # Context first if required
            if self.displaycontextfirst:
                contexttext = QtGui.QPushButton(widget)
                contexttext.setCursor(QtCore.Qt.PointingHandCursor)
                contexttext.setStyleSheet("border: None; Font-size: 8px; text-align:left")
                contexttext.setText("@"+context)
                contexttext.setMinimumWidth(50)
                contexttext.setMaximumWidth(50)
                horizontalLayout.addWidget(contexttext)
                self.itemContextButtonMapper.setMapping(contexttext, context_id)
                contexttext.clicked.connect(self.itemContextButtonMapper.map)
                
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
                    dueText.setStyleSheet("Font-size: 8px; color: black; Background-color: 'orange'")
    
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
            
            # Add Context Button
            if context != None and not self.displaycontextfirst:
                contextButton = QtGui.QPushButton(widget)
                font = QtGui.QFont()
                font.setPointSize(7)
                contextButton.setFont(font)
                contextButton.setText("[c]")
                contextButton.setToolTip("context: @" + context)
                contextButton.setCursor(QtCore.Qt.PointingHandCursor)
                contextButton.setStyleSheet("border: None;")
                horizontalLayout.addWidget(contextButton)
                self.itemContextButtonMapper.setMapping(contextButton, context_id) #TODO fix
                contextButton.clicked.connect(self.itemContextButtonMapper.map)
                
            # Add project button
            if project != None and not self.displayprojectfirst:
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
        
        # set size of the list to be exactly enough for its contents
        contentMargins = self.listWidget.getContentsMargins()
        self.listWidget.setFixedHeight(count*22+contentMargins[1]+contentMargins[3])  
        #self.listWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            
    def deleteItemButtonClicked(self, id):
        logging.info("TracksActionList->deleteItemButtonClicked  -  " + str(id))
        reallydelete = QtGui.QMessageBox.question(self, "tracks.cute: Really Delete", "Are you sure you want to delete this action?" +str(id), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        logging.debug("TracksActionList->deleteItemButtonClicked, reallydelete=" + str(reallydelete==QtGui.QMessageBox.Yes))
        
        if reallydelete==QtGui.QMessageBox.Yes:
            # Remove the action
            sql = "DELETE FROM todos WHERE id=?"
            self.databaseCon.execute(sql, (id,))
            
            # Remove associated dependencies
            sqlassoc = "DELETE FROM dependencies WHERE successor_id=? OR predecessor_id=?"
            self.databaseCon.execute(sqlassoc, (id,id,))
            
            self.databaseCon.commit()
            
            self.emit(QtCore.SIGNAL("actionModified()"))
        
    def editItemButtonClicked(self, id):
        logging.info("TracksActionList->editItemButtonClicked  -  " + str(id))
        self.emit(QtCore.SIGNAL("editAction(int)"),id)

        
    def starItemButtonClicked(self, id):
        logging.info("TracksActionList->starItemButtonClicked  -  " + str(id))
        
        query = "select todos.description, tags.name from todos, tags, taggings where todos.id=taggings.taggable_id and tags.id = taggings.tag_id and tags.name='starred' and todos.id=?"
        data = self.databaseCon.execute(query, [id,]).fetchall()
        
        if len(data) == 0:
            # make sure tags contains "starred"
            query_for_starred = "select tags.id from tags where tags.name='starred'"
            data_for_starred = self.databaseCon.execute(query_for_starred).fetchall()
            if len(data_for_starred) == 0:
                insert_tag_query = "insert into tags values(NULL, 'starred', DATETIME('now'), DATETIME('now'))"
                self.databaseCon.execute(insert_tag_query)
                self.databaseCon.commit()
            # tag the todo as "starred"
            insert_tagging_query = "insert into taggings values(NULL, ?, (SELECT id from tags where name = 'starred'), 'Todo')"
            self.databaseCon.execute(insert_tagging_query, (id,))
            self.databaseCon.commit()
        else:
            # the todo is already tagged as starred, remove the tag
            remove_tagging_query = "delete from taggings where taggable_id=?"
            self.databaseCon.execute(remove_tagging_query, (id,))
            self.databaseCon.commit()
        self.emit(QtCore.SIGNAL("actionModified()"))
        
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
        
    def contextItemButtonClicked(self, id):
        logging.info("TracksActionList->contextItemButtonClicked  -  " +str(id))
        self.emit(QtCore.SIGNAL("gotoContext(int)"), id)
        
    def refresh(self):
        logging.info("TracksActionList->refresh")
        self.listWidget.clear()
        self.fillList()
        
    def setDBQuery(self, dbQuery):
        logging.info("TracksActionList->setDBQuery")
        self.dbQuery = dbQuery
        self.refresh()
        
    def setExpanded(self, expanded):
        logging.info("TracksActionList->setExpanded")
        
        buttonIcon = None
        if QtGui.QIcon.hasThemeIcon("go-up"):
            buttonIcon = QtGui.QIcon.fromTheme("go-up")
        else:
            buttonIcon = QtGui.QIcon(self.iconPath + "go-up.png")
            
        if not expanded:
            if QtGui.QIcon.hasThemeIcon("go-down"):
                buttonIcon = QtGui.QIcon.fromTheme("go-down")
            else:
                buttonIcon = QtGui.QIcon(self.iconPath + "go-down.png")
        self.toggleListButton.setIcon(QtGui.QIcon(buttonIcon.pixmap(16,16,1,0)))
        
        self.toggleListButton.setChecked(expanded)
        self.listWidget.setVisible(expanded)


class CustomButton(QtGui.QPushButton):
    __pyqtSignals__ = ("ctrlclicked()",
                     )
    ctrlclicked = QtCore.pyqtSignal()
    
    def __init__(self):
        QtGui.QPushButton.__init__(self)
    def mousePressEvent(self,event):
        if event.modifiers()==QtCore.Qt.ControlModifier:
            self.emit(QtCore.SIGNAL("ctrlclicked()"))
        else:
            QtGui.QPushButton.mousePressEvent(self,event)
        
        
class DumbWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
    def mousePressEvent(self, event):
        print "clicked"
