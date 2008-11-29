#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    src/mainwindow.py
#
#    Copyright (C) 2008 Konstantin Grigoriev
#
#    This file is part of qsmile.
#    
#    qsmile is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    qsmile is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with qsmile.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Module implementing MainWindow.
"""

import os
import tempfile
from shutil import copyfile, rmtree
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from model import Pack, Icon
from common import ModeForm
from util import log
from exportpack import export_pidgin, export_kopete, export_qip, export_all
from importpack import import_kopete, import_pidgin_zip, import_pidgin_folder, import_qip_zip
import config

from ui.Ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow, ModeForm):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        ModeForm.__init__(self)
        self.setupUi(self)
        self.movie = None
        self.movieList = []
        self.currentSmile = None
        self.pack = None

    def initTempDir(self):
        if config.temp_dir:
            rmtree(config.temp_dir)
        config.temp_dir = tempfile.mkdtemp()
    
    def fillTable(self):
        self.clearSmileDetail()
        self.clearSmileList()
        self.actionClose_pack.setEnabled(True) 
        self.menuExport.setEnabled(True)
        self.packBox.setEnabled(True)
        self.smileListBox.setEnabled(True)
        self.nameEdit.setText(self.pack.name)
        self.authorEdit.setText(self.pack.author)
        self.versionEdit.setText(self.pack.version)
        for i in range(len(self.pack.icons)):
            self.table.insertRow(i)
            self.fillTableRow(i)
        self.table.selectRow(0)
            
    def fillTableRow(self, row):
        icon = self.pack.icons[row]
        movieLabel = QtGui.QLabel()
        if icon and icon.image and os.path.exists(os.path.join(config.temp_dir, icon.image)):
            if row >= len(self.movieList):
                self.movieList.append(QtGui.QMovie(os.path.join(config.temp_dir, icon.image)))
            else:
                self.movieList[row] = QtGui.QMovie(os.path.join(config.temp_dir, icon.image))
            movieLabel.setMovie(self.movieList[row])
            movieLabel.movie().start()
        self.table.setCellWidget(row, 0, movieLabel)
        self.table.setCellWidget(row, 1, QtGui.QLabel(icon.image))
        self.table.setCellWidget(row, 2, QtGui.QLabel(" ".join(icon.text)))
        
    def clearTableRow(self,  row):
        self.table.cellWidget(row, 0).movie().stop()
        self.table.cellWidget(row, 0).clear()
        self.table.removeCellWidget(row, 0)
        self.table.removeCellWidget(row, 1)
        self.table.removeCellWidget(row, 2)
        self.movieList[row] = None

    @pyqtSignature("")
    def on_upSmileButton_clicked(self):
        if self.table.currentRow() > 0:
            self.moveSmile(lambda row: row - 1)
            
    @pyqtSignature("")
    def on_downSmileButton_clicked(self):
        if self.table.currentRow() < self.table.rowCount() - 1:
            self.moveSmile(lambda row: row + 1)
            
    def moveSmile(self, move):
        row = self.table.currentRow()
        self.clearSmileDetail()
        self.clearTableRow(row)
        self.clearTableRow(move(row))
        # change filenames
        os.rename(os.path.join(config.temp_dir, self.pack.icons[row].image), os.path.join(config.temp_dir, self.pack.icons[row].image + ".tmp"))
        os.rename(os.path.join(config.temp_dir, self.pack.icons[move(row)].image), os.path.join(config.temp_dir, self.pack.icons[row].image))
        os.rename(os.path.join(config.temp_dir, self.pack.icons[row].image) + ".tmp", os.path.join(config.temp_dir, self.pack.icons[move(row)].image))
        self.pack.icons[row].image , self.pack.icons[move(row)].image = self.pack.icons[move(row)].image , self.pack.icons[row].image        
        # changing rows in pack
        self.pack.icons[row] , self.pack.icons[move(row)] = self.pack.icons[move(row)] , self.pack.icons[row]        
        self.fillTableRow(row)
        self.fillTableRow(move(row))        
        self.table.selectRow(move(row))

    @pyqtSignature("")
    def on_addSmileButton_clicked(self):
        self.currentSmile = Icon([], self.pack.generate_icon_filename())
        self.setCreateMode()
        self.fillSmileDetail()
        
    @pyqtSignature("")
    def on_editSmileButton_clicked(self):    
        self.currentSmile = self.pack.icons[self.table.currentRow()]
        self.setEditMode()
        self.fillSmileDetail()
       
    @pyqtSignature("")
    def on_removeSmileButton_clicked(self):
        if not QtGui.QMessageBox.question(self, "Are you sure?", "Are you sure?", "Yes", "No"):
            self.table.scrollToTop()
            row = self.table.currentRow()
            self.clearSmileDetail()
            self.table.selectRow(row - 1)
            icon = self.pack.icons[row]
            self.clearTableRow(row)
            self.table.removeRow(row)
            if icon and icon.image and os.path.exists(os.path.join(config.temp_dir, icon.image)):
                os.remove(os.path.join(config.temp_dir, icon.image))
            self.pack.delete_icon(row)
            
    @pyqtSignature("int, int, int, int")
    def on_table_currentCellChanged(self, currentRow, currentColumn, previousRow, previousColumn):
        if currentRow != -1:
            self.upSmileButton.setEnabled(currentRow > 0)
            self.downSmileButton.setEnabled(currentRow < self.table.rowCount() - 1)
            self.removeSmileButton.setEnabled(True)
            self.editSmileButton.setEnabled(True)
            self.currentSmile = self.pack.icons[currentRow]
            self.setViewMode()
            self.fillSmileDetail()
        
    @pyqtSignature("int, int")
    def on_table_cellDoubleClicked(self, currentRow, currentColumn):
        self.currentSmile = self.pack.icons[self.table.currentRow()]
        self.setEditMode()
        self.fillSmileDetail()
        
    @pyqtSignature("")
    def on_changeImageButton_clicked(self):
        imageFile = QtGui.QFileDialog.getOpenFileName(self, "Choose picture", os.path.expanduser('~'), "gif (*.gif)")
        if imageFile:
            log.debug("Opening image : %s", imageFile)
            self.movieLabel.clear()
            self.movie = QtGui.QMovie(imageFile)
            self.movieLabel.setMovie(self.movie)
            self.movieLabel.movie().start()
    
    @pyqtSignature("")
    def on_removeTextButton_clicked(self):
        self.textList.removeItemWidget(self.textList.takeItem(self.textList.currentRow()))
    
    @pyqtSignature("")
    def on_addTextButton_clicked(self):
        self.textList.addItem("")
        self.textList.setCurrentRow(self.textList.count()-1)
        self.textEdit.setFocus()
    
    @pyqtSignature("")
    def on_textList_itemSelectionChanged(self):
        if self.textList.count() != 0:
            self.removeTextButton.setEnabled(True)
            self.textEdit.setEnabled(True)
            self.textEdit.setText(self.textList.currentItem().text())
            self.textEdit.setFocus()
        else:
            self.removeTextButton.setEnabled(False)
            self.textEdit.setEnabled(False)
            
    @pyqtSignature("QString")
    def on_textEdit_textEdited(self, newText):
        if "," in str(self.textEdit.text()):
            self.textEdit.setText(str(self.textEdit.text()).replace(",",""))    
        else:
            self.textList.currentItem().setText(self.textEdit.text())
    
    @pyqtSignature("")
    def on_saveTextButton_clicked(self):
        if "," in str(self.textEdit.text()):
            QtGui.QMessageBox.warning(self, "Wrong character in smile text", "Wrong character in smile text", "Ok")
        else:
            self.textList.currentItem().setText(self.textEdit.text())
    
    @pyqtSignature("")
    def on_saveButton_clicked(self):
        self.currentSmile.text = []
        for i in range(self.textList.count()):
            self.currentSmile.text.append(str(self.textList.item(i).text()))
        if self.currentSmile.validate_icon():
            # copying image      
            if self.currentSmile.image == None or self.movie.fileName() != os.path.join(config.temp_dir, self.currentSmile.image): 
                log.debug(" new image fileName : %s", self.movie.fileName())
                copyfile(self.movie.fileName(), os.path.join(config.temp_dir, self.currentSmile.image))
            # updating text
            log.debug(" new text : %s", self.currentSmile.text)
            if self.isCreateMode():
                self.pack.add_icon(self.currentSmile)
                self.table.insertRow(self.table.rowCount())
                self.table.selectRow(self.table.rowCount() - 1)
            self.setViewMode()
            self.fillTableRow(self.table.currentRow())
            self.switchForm()
        else:
            QtGui.QMessageBox.warning(self, "Can't save empty smile", "Can't save empty smile", "Ok")
    
    @pyqtSignature("")        
    def on_cancelButton_clicked(self):
        self.currentSmile = self.pack.icons[self.table.currentRow()]
        self.setViewMode()
        self.fillSmileDetail()
        
    def clearSmileDetail(self):
        if self.movieLabel.movie():
            self.movieLabel.movie().stop()
        self.movieLabel.clear()        
        if self.movie:
            self.movie.stop()
            self.movie = None
        self.textList.clear()
        self.textEdit.clear()
        self.removeTextButton.setEnabled(False)
        self.textEdit.setEnabled(False)  
               
    def fillSmileDetail(self):
        log.debug("selected icon : %s",  self.currentSmile)
        self.switchForm()
        self.clearSmileDetail()
        # setting movie
        if self.currentSmile and self.currentSmile.image and os.path.exists(os.path.join(config.temp_dir, self.currentSmile.image)):
            self.movie = QtGui.QMovie(os.path.join(config.temp_dir, self.currentSmile.image))
            self.movieLabel.setMovie(self.movie)
            self.movieLabel.movie().start()
        # setting text
        if self.currentSmile and self.currentSmile.text:          
            self.textList.addItems(self.currentSmile.text)
            self.textList.setCurrentRow(0)
            self.textEdit.setText(self.textList.currentItem().text())
    
    def clearSmileList(self):
        self.nameEdit.clear()
        self.authorEdit.clear()
        self.versionEdit.clear()
        self.table.clearContents()
        self.table.setRowCount(0)
        self.movieList = []
        self.upSmileButton.setEnabled(False)
        self.downSmileButton.setEnabled(False)
        self.removeSmileButton.setEnabled(False)
        self.editSmileButton.setEnabled(False)
            
    def clearAll(self):
        self.clearSmileDetail()
        self.clearSmileList()
        self.menuExport.setEnabled(False)
        self.actionClose_pack.setEnabled(False)
        self.packBox.setEnabled(False)
        self.smileListBox.setEnabled(False)
        self.smileDetailBox.setEnabled(False)
        
    def closePack(self):
        self.clearAll()
        self.currentSmile = None
        self.pack = None
        if config.temp_dir:
            rmtree(config.temp_dir)
            config.temp_dir = None

    def switchForm(self):
        self.smileDetailBox.setEnabled(not self.isViewMode())
        self.smileListBox.setEnabled(self.isViewMode())        

    @pyqtSignature("")
    def on_actionClose_pack_triggered(self):
        self.closePack()

    @pyqtSignature("")
    def on_actionNew_pack_triggered(self):
        self.clearAll()
        self.initTempDir()
        self.pack = Pack()
        self.fillTable()

    @pyqtSignature("")
    def on_actionExport_To_Kopete_triggered(self):
        targetFile = QtGui.QFileDialog.getSaveFileName(self, "Export to Kopete JISP", self.pack.name + ".jisp", "Kopete Smile Pack JISP (*.jisp)")
        if targetFile:
            export_kopete(self.pack, str(targetFile))
        
    @pyqtSignature("")
    def on_actionExport_To_Pidgin_triggered(self):
        targetFile = QtGui.QFileDialog.getSaveFileName(self, "Export to Pidgin ZIP", self.pack.name + "_pidgin.zip", "Pidgin Smile Pack ZIP (*.zip)")
        if targetFile:    
            export_pidgin(self.pack, str(targetFile))
        
    @pyqtSignature("")
    def on_actionExport_To_Qip_triggered(self):
        targetFile = QtGui.QFileDialog.getSaveFileName(self, "Export to QIP ZIP", self.pack.name + "_qip.zip", "QIP Smile Pack ZIP (*.zip)")
        if targetFile:
            export_qip(self.pack, str(targetFile))

    @pyqtSignature("")
    def on_actionExport_To_All_triggered(self):
        targetDir = QtGui.QFileDialog.getExistingDirectory(self, "Export to All", os.path.expanduser('~'))
        if targetDir:
            export_all(self.pack, str(targetDir))
        
    @pyqtSignature("")
    def on_actionImport_From_Kopete_triggered(self):
        targetFile = QtGui.QFileDialog.getOpenFileName(self, "Import From Kopete JISP", os.path.expanduser('~'), "Kopete Smile Pack JISP (*.jisp)")
        if targetFile:
            self.closePack()
            self.initTempDir()
            self.pack = import_kopete(str(targetFile))
            self.fillTable()

    @pyqtSignature("")
    def on_actionImport_From_Pidgin_ZIP_triggered(self):
        targetFile = QtGui.QFileDialog.getOpenFileName(self, "Import From Pidgin ZIP", os.path.expanduser('~'), "Pidgin Smile Pack ZIP (*.zip)")
        if targetFile:
            self.closePack()
            self.initTempDir()
            self.pack = import_pidgin_zip(str(targetFile))
            self.fillTable()
    
    @pyqtSignature("")        
    def on_actionImport_From_Pidgin_Folder_triggered(self):
        targetDir = QtGui.QFileDialog.getExistingDirectory(self, "Import From Pidgin Folder", os.path.expanduser('~'))
        if targetDir:
            self.closePack()
            self.initTempDir()
            self.pack = import_pidgin_folder(str(targetDir))
            self.fillTable()
            
    @pyqtSignature("")
    def on_actionImport_From_QIP_ZIP_triggered(self):
        targetFile = QtGui.QFileDialog.getOpenFileName(self, "Import From QIP ZIP", os.path.expanduser('~'), "QIP Smile Pack ZIP (*.zip)")
        if targetFile:
            self.closePack()
            self.initTempDir()
            self.pack = import_qip_zip(str(targetFile))
            self.fillTable()
