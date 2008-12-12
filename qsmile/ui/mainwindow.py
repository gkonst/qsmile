# -*- coding: utf-8 -*-
#
#    qsmile/core/mainwindow.py
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
from qsmile.core.model import Pack, Icon
from qsmile.core.common import ModeForm
from qsmile.core.util import log
from qsmile.core.exportpack import export_pidgin, export_kopete, export_qip, export_all
from qsmile.core.importpack import import_kopete, import_pidgin_zip, import_pidgin_dir, import_qip_zip, import_qip_dir, ImportPackError
import qsmile.core.config as config

from qsmile.ui.Ui_mainwindow import Ui_MainWindow

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

    def _init_temp_dir(self):
        if config.temp_dir:
            log.debug("cleaning temp_dir : %s",  config.temp_dir)
            rmtree(config.temp_dir)
        config.temp_dir = tempfile.mkdtemp()
        log.debug("using temp_dir : %s",  config.temp_dir)
    
    def _fill_table(self):
        self._clear_smile_detail()
        self._clear_smile_list()
        self.close_pack_action.setEnabled(True) 
        self.export_menu.setEnabled(True)
        self.packBox.setEnabled(True)
        self.smileListBox.setEnabled(True)
        self.nameEdit.setText(self.pack.name)
        self.authorEdit.setText(self.pack.author)
        self.versionEdit.setText(self.pack.version)
        for i in range(len(self.pack.icons)):
            self.table.insertRow(i)
            self._fill_table_row(i)
        self.table.selectRow(0)
            
    def _fill_table_row(self, row):
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
        
    def _clear_table_row(self,  row):
        self.table.cellWidget(row, 0).movie().stop()
        self.table.cellWidget(row, 0).clear()
        self.table.removeCellWidget(row, 0)
        self.table.removeCellWidget(row, 1)
        self.table.removeCellWidget(row, 2)
        self.movieList[row] = None

    @pyqtSignature("")
    def on_upSmileButton_clicked(self):
        if self.table.currentRow() > 0:
            self._move_smile(lambda row: row - 1)
            
    @pyqtSignature("")
    def on_downSmileButton_clicked(self):
        if self.table.currentRow() < self.table.rowCount() - 1:
            self._move_smile(lambda row: row + 1)
            
    def _move_smile(self, move):
        row = self.table.currentRow()
        self._clear_smile_detail()
        self._clear_table_row(row)
        self._clear_table_row(move(row))
        # change filenames
        os.rename(os.path.join(config.temp_dir, self.pack.icons[row].image), os.path.join(config.temp_dir, self.pack.icons[row].image + ".tmp"))
        os.rename(os.path.join(config.temp_dir, self.pack.icons[move(row)].image), os.path.join(config.temp_dir, self.pack.icons[row].image))
        os.rename(os.path.join(config.temp_dir, self.pack.icons[row].image) + ".tmp", os.path.join(config.temp_dir, self.pack.icons[move(row)].image))
        self.pack.icons[row].image , self.pack.icons[move(row)].image = self.pack.icons[move(row)].image , self.pack.icons[row].image        
        # changing rows in pack
        self.pack.icons[row] , self.pack.icons[move(row)] = self.pack.icons[move(row)] , self.pack.icons[row]        
        self._fill_table_row(row)
        self._fill_table_row(move(row))        
        self.table.selectRow(move(row))
        
    def _fill_smile_detail(self):
        log.debug("selected icon : %s",  self.currentSmile)
        self._switch_form()
        self._clear_smile_detail()
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

    def _clear_smile_detail(self):
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
    
    def _clear_smile_list(self):
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
            
    def _clear_all(self):
        self._clear_smile_detail()
        self._clear_smile_list()
        self.export_menu.setEnabled(False)
        self.close_pack_action.setEnabled(False)
        self.packBox.setEnabled(False)
        self.smileListBox.setEnabled(False)
        self.smileDetailBox.setEnabled(False)
        
    def _close_pack(self):
        self._clear_all()
        self.currentSmile = None
        self.pack = None
        if config.temp_dir:
            rmtree(config.temp_dir)
            config.temp_dir = None

    def _switch_form(self):
        self.smileDetailBox.setEnabled(not self.isViewMode())
        self.smileListBox.setEnabled(self.isViewMode())  

    @pyqtSignature("")
    def on_addSmileButton_clicked(self):
        self.currentSmile = Icon([], self.pack.generate_icon_filename())
        self.setCreateMode()
        self._fill_smile_detail()
        
    @pyqtSignature("")
    def on_editSmileButton_clicked(self):    
        self.currentSmile = self.pack.icons[self.table.currentRow()]
        self.setEditMode()
        self._fill_smile_detail()
       
    @pyqtSignature("")
    def on_removeSmileButton_clicked(self):
        if not QtGui.QMessageBox.question(self, "Are you sure?", "Are you sure?", "Yes", "No"):
            self.table.scrollToTop()
            row = self.table.currentRow()
            self._clear_smile_detail()
            self.table.selectRow(row - 1)
            icon = self.pack.icons[row]
            self._clear_table_row(row)
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
            self._fill_smile_detail()
        
    @pyqtSignature("int, int")
    def on_table_cellDoubleClicked(self, currentRow, currentColumn):
        self.currentSmile = self.pack.icons[self.table.currentRow()]
        self.setEditMode()
        self._fill_smile_detail()
        
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
            self._fill_table_row(self.table.currentRow())
            self._switch_form()
        else:
            QtGui.QMessageBox.warning(self, "Can't save empty smile", "Can't save empty smile", "Ok")
    
    @pyqtSignature("")        
    def on_cancelButton_clicked(self):
        self.currentSmile = self.pack.icons[self.table.currentRow()]
        self.setViewMode()
        self._fill_smile_detail()     

    @pyqtSignature("")
    def on_close_pack_action_triggered(self):
        self._close_pack()

    @pyqtSignature("")
    def on_new_pack_action_triggered(self):
        self._close_pack()
        self._init_temp_dir()
        self.pack = Pack()
        self._fill_table()

    @pyqtSignature("")
    def on_export_to_kopete_action_triggered(self):
        targetFile = QtGui.QFileDialog.getSaveFileName(self, "Export to Kopete JISP", os.path.join(os.path.expanduser('~'), self.pack.name + ".jisp"), "Kopete Smile Pack JISP (*.jisp)")
        if targetFile:
            export_kopete(self.pack, str(targetFile))
        
    @pyqtSignature("")
    def on_export_to_pidgin_action_triggered(self):
        targetFile = QtGui.QFileDialog.getSaveFileName(self, "Export to Pidgin ZIP", os.path.join(os.path.expanduser('~'), self.pack.name + "_pidgin.zip"), "Pidgin Smile Pack ZIP (*.zip)")
        if targetFile:    
            export_pidgin(self.pack, str(targetFile))
        
    @pyqtSignature("")
    def on_export_to_qip_action_triggered(self):
        targetFile = QtGui.QFileDialog.getSaveFileName(self, "Export to QIP ZIP", os.path.join(os.path.expanduser('~'), self.pack.name + "_qip.zip"), "QIP Smile Pack ZIP (*.zip)")
        if targetFile:
            export_qip(self.pack, str(targetFile))

    @pyqtSignature("")
    def on_export_to_all_action_triggered(self):
        targetDir = QtGui.QFileDialog.getExistingDirectory(self, "Export to All", os.path.expanduser('~'))
        if targetDir:
            export_all(self.pack, str(targetDir))
        
    @pyqtSignature("")
    def on_import_from_kopete_action_triggered(self):
        targetFile = QtGui.QFileDialog.getOpenFileName(self, "Import From Kopete JISP", os.path.expanduser('~'), "Kopete Smile Pack JISP (*.jisp)")
        if targetFile:
            self._close_pack()
            self._init_temp_dir()
            try:
                self.pack = import_kopete(str(targetFile))
                self._fill_table()
            except ImportPackError, e:
                QtGui.QMessageBox.warning(self, "Error", e.message, "Ok")

    @pyqtSignature("")
    def on_import_from_pidgin_zip_action_triggered(self):
        targetFile = QtGui.QFileDialog.getOpenFileName(self, "Import From Pidgin ZIP", os.path.expanduser('~'), "Pidgin Smile Pack ZIP (*.zip)")
        if targetFile:
            self._close_pack()
            self._init_temp_dir()
            try:
                self.pack = import_pidgin_zip(str(targetFile))
                self._fill_table()
            except ImportPackError, e:
                QtGui.QMessageBox.warning(self, "Error", e.message, "Ok")
    
    @pyqtSignature("")        
    def on_import_from_pidgin_dir_action_triggered(self):
        targetDir = QtGui.QFileDialog.getExistingDirectory(self, "Import From Pidgin Folder", os.path.expanduser('~'))
        if targetDir:
            self._close_pack()
            self._init_temp_dir()
            try:
                self.pack = import_pidgin_dir(str(targetDir))
                self._fill_table()
            except ImportPackError, e:
                QtGui.QMessageBox.warning(self, "Error", e.message, "Ok")
                            
    @pyqtSignature("")
    def on_import_from_qip_zip_action_triggered(self):
        targetFile = QtGui.QFileDialog.getOpenFileName(self, "Import From QIP ZIP", os.path.expanduser('~'), "QIP Smile Pack ZIP (*.zip)")
        if targetFile:
            self._close_pack()
            self._init_temp_dir()
            try:
                self.pack = import_qip_zip(str(targetFile))
                self._fill_table()
            except ImportPackError, e:
                QtGui.QMessageBox.warning(self, "Error", e.message, "Ok")
            
    @pyqtSignature("")        
    def on_import_from_qip_dir_action_triggered(self):
        targetDir = QtGui.QFileDialog.getExistingDirectory(self, "Import From QIP Folder", os.path.expanduser('~'))
        if targetDir:
            self._close_pack()
            self._init_temp_dir()
            try:
                self.pack = import_qip_dir(str(targetDir))
                self._fill_table()
            except ImportPackError, e:
                QtGui.QMessageBox.warning(self, "Error", e.message, "Ok")
            
