#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
## \package sardanaclient nexdatas
## \file SardanaWriterDlg.py
# Dialog class for Sardana Writer Client

from PyQt4.QtCore import (SIGNAL, QString)
from PyQt4.QtGui import (QMessageBox,QDialog)
from ui_sardanawriterdlg import  Ui_SardanaWriterDlg



## dialog defining an attribute
class SardanaWriterDlg(QDialog, Ui_SardanaWriterDlg):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(SardanaWriterDlg, self).__init__(parent)


    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):
        self.setupUi(self)

        self.connect(self.closePushButton, SIGNAL("clicked()"), self.accept)     
        
    ## updates the file name     
    def updateFile(self,fname):
        self.fileLabel.setText("File: %s" % fname) 


    ## updates the nexus writer device name
    def updateNWriter(self, text):
        self.nwLabel.setText("Nexus Writer: %s" % text) 

    ## updates the configuration server device name
    def updateCServer(self, text):
        self.csLabel.setText("Configuration server: %s" % text) 


    ## updates the configuration server device name
    def updateNP(self, iscan, np):
        self.ofLabel.setText("Step: %s of %s" %  (iscan, np)) 


if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    ## Qt application
    app = QApplication(sys.argv)
    ## attribute form
    form = SardanaWriterDlg()
    form.createGUI()
    form.show()
    app.exec_()
