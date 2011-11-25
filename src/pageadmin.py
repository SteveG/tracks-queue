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

from PyQt4 import QtGui
from PyQt4 import QtCore
import logging
from widgetActionEditor import WidgetActionEditor
from widgetActionList import WidgetActionList

class PageAdmin(QtGui.QWidget):
    userChanged = QtCore.pyqtSignal(int)
    
    def __init__(self, parent, databaseCon):
        logging.info("PageAdmin->__init__(self, parent, databaseCon)")
        QtGui.QWidget.__init__(self, parent)
        self.databaseCon = databaseCon
        self.settings = QtCore.QSettings("tracks-queue", "tracks-queue")
        #latitudeLabel = QtGui.QLabel("Latitude:")
        #layout = QtGui.QGridLayout(self)
        #layout.addWidget(latitudeLabel, 0, 0)
        
        # The main page layout
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        
        # Scroll area for lists
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        
        # Layout for scroll area
        widget = QtGui.QWidget()
        self.scrollArea.setWidget(widget)
        self.verticalLayout = QtGui.QVBoxLayout(widget)
        
        self.horizontalLayout.addWidget(self.scrollArea)      
    
        # user select
        userSelHozLayout = QtGui.QHBoxLayout(self)
        userSelLabel = QtGui.QLabel("User Select")
        self.userSelCombo = QtGui.QComboBox(self)
        userSelHozLayout.addWidget(userSelLabel)
        userSelHozLayout.addWidget(self.userSelCombo)
        userSelHozLayout.addItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.verticalLayout.addLayout(userSelHozLayout)
        
        self.current_user_id = None
        if self.settings.contains("database/user"):
            self.current_user_id = int(self.settings.value("database/user").toString())
        
        self.userSelCombo.currentIndexChanged.connect(self.userSelectChanged)
        
        
        # Add a vertical spacer
        spacerItem = QtGui.QSpacerItem(
            1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
    def refresh(self):
        logging.info("PageAdmin->refresh()")
        
        self.userSelCombo.currentIndexChanged.disconnect(self.userSelectChanged)
        self.userSelCombo.clear()
        data = self.databaseCon.execute("SELECT login, id FROM users ORDER BY login")
        for item in data:
            self.userSelCombo.addItem(item[0], item[1])
            
        founduser = False
        if self.current_user_id:
            index = self.userSelCombo.findData(self.current_user_id)
            if index:
                self.userSelCombo.setCurrentIndex(index)
                founduser = True

        if not founduser:
            self.userSelCombo.setCurrentIndex(0)
            self.userSelectChanged()
            #self.current_user_id = self.settingsUserSelectBox.itemData(0).toInt()[0]
            #self.settings.setValue("database/user", QtCore.QVariant(self.current_user_id))
            
        self.userSelCombo.currentIndexChanged.connect(self.userSelectChanged)

    def userSelectChanged(self):
        logging.info("PageAdmin->userSelectChanged()")
        self.current_user_id = self.userSelCombo.itemData(self.userSelCombo.currentIndex()).toInt()[0]
        self.settings.setValue("database/user", QtCore.QVariant(self.current_user_id))
        self.emit(QtCore.SIGNAL("userChanged(int)"), self.current_user_id)
