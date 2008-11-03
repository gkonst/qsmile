# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

import os
import tempfile
from shutil import copyfile
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from exportpack import exportPidgin, exportKopete, exportQip, exportAll
from importpack import importKopete, importPidginZip, importQipZip
import options

from ui.Ui_MainWindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)       
        #options.TEMP_DIR = tempfile.mkdtemp()
    
    def fillTable(self):
        print "options.TEMP_DIR : ", options.TEMP_DIR 
        self.menuExport.setEnabled(True)
        self.packBox.setEnabled(True)
        self.smileListBox.setEnabled(True)
        self.nameEdit.setText(self.pack.name)
        self.authorEdit.setText(self.pack.author)
        self.versionEdit.setText(self.pack.version)
        self.table.setRowCount(len(self.pack.icons))
        self.movieList = []
        for i in range(len(self.pack.icons)):
            self.fillTableRow(i)
        self.table.setCurrentCell(0, 0)
            
    def fillTableRow(self, row):
        icon = self.pack.icons[row]
        movieLabel = QtGui.QLabel()
        if icon and icon.image and os.path.exists(os.path.join(options.TEMP_DIR, icon.image)):
            if row >= len(self.movieList):
                self.movieList.append(QtGui.QMovie(os.path.join(options.TEMP_DIR, icon.image)))
            else:
                self.movieList[row] = QtGui.QMovie(os.path.join(options.TEMP_DIR, icon.image))
            movieLabel.setMovie(self.movieList[row])
            movieLabel.movie().start()
        self.table.setCellWidget(row, 0, movieLabel)
        self.table.setCellWidget(row, 1, QtGui.QLabel(icon.image))
        self.table.setCellWidget(row, 2, QtGui.QLabel(" ".join(icon.text)))

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
        # change filenames
        os.rename(os.path.join(options.TEMP_DIR, self.pack.icons[row].image), os.path.join(options.TEMP_DIR, self.pack.icons[row].image + ".tmp"))
        os.rename(os.path.join(options.TEMP_DIR, self.pack.icons[move(row)].image), os.path.join(options.TEMP_DIR, self.pack.icons[row].image))
        os.rename(os.path.join(options.TEMP_DIR, self.pack.icons[row].image) + ".tmp", os.path.join(options.TEMP_DIR, self.pack.icons[move(row)].image))
        self.pack.icons[row].image , self.pack.icons[move(row)].image = self.pack.icons[move(row)].image , self.pack.icons[row].image        
        # changing rows in pack
        self.pack.icons[row] , self.pack.icons[move(row)] = self.pack.icons[move(row)] , self.pack.icons[row]        
        self.fillTableRow(row)
        self.fillTableRow(move(row))        
        self.table.setCurrentCell(move(row), 0)

    @pyqtSignature("")
    def on_addSmileButton_clicked(self):
        self.pack.addIcon(None)
        self.table.insertRow(self.table.rowCount())
        self.table.setCurrentCell(self.table.rowCount() - 1, 0)
        self.showItem(True)
        
    @pyqtSignature("")
    def on_removeSmileButton_clicked(self):
        if not QtGui.QMessageBox.question(self, "Are you sure?", "Are you sure?", "Yes", "No"):
            icon = self.pack.icons[self.table.currentRow()]
            #self.table.cellWidget(self.table.currentRow(), 0).clear()
            #del self.movieList[self.table.currentRow()]
            self.table.removeRow(self.table.currentRow())
            if icon and icon.image and os.path.exists(os.path.join(options.TEMP_DIR, icon.image)):
                os.remove(os.path.join(options.TEMP_DIR, icon.image))
            self.pack.deleteIcon(self.table.currentRow())
            
    @pyqtSignature("int, int, int, int")
    def on_table_currentCellChanged(self, currentRow, currentColumn, previousRow, previousColumn):
        self.upSmileButton.setEnabled(currentRow > 0)
        self.downSmileButton.setEnabled(currentRow < self.table.rowCount() - 1)
        self.removeSmileButton.setEnabled(True)
        self.showItem()
        
    @pyqtSignature("int, int")
    def on_table_cellDoubleClicked(self, currentRow, currentColumn):
        self.showItem(True)
        
    @pyqtSignature("")
    def on_changeImageButton_clicked(self):
        imageFile = QtGui.QFileDialog.getOpenFileName(self, "Choose picture", os.path.expanduser('~'), "gif (*.gif)")
        if imageFile:
            print "Opening image : ", imageFile
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
        self.textEdit.setText(self.textList.currentItem().text())
        self.textEdit.setFocus()
    
    @pyqtSignature("")
    def on_saveTextButton_clicked(self):
        if "," in str(self.textEdit.text()):
            QtGui.QMessageBox.warning(self, "Wrong character in smile text", "Wrong character in smile text", "Ok")
        else:
            self.textList.currentItem().setText(self.textEdit.text())
    
    @pyqtSignature("")
    def on_saveButton_clicked(self):
        icon = self.pack.icons[self.table.currentRow()]
        # copying image      
        if icon.image == None or self.movie.fileName() != os.path.join(options.TEMP_DIR, icon.image): 
            print "fileName : ", self.movie.fileName()
            copyfile(os.path.join(options.TEMP_DIR, icon.image), os.path.join(options.TEMP_DIR, icon.image + ".bak"))  
            copyfile(self.movie.fileName(), os.path.join(options.TEMP_DIR, icon.image))
        # updating text
        icon.text = []
        #icon.text = map(lambda item: str(item.text()), self.textList.items(None))
        for i in range(self.textList.count()):
            icon.text.append(str(self.textList.item(i).text()))
        print icon.text
        self.fillTableRow(self.table.currentRow())
    
    @pyqtSignature("")        
    def on_cancelButton_clicked(self):
        self.showItem()
        
    def showItem(self, editFlag=False):
        icon = self.pack.icons[self.table.currentRow()]
        print "selected icon : ",  icon
        self.smileDetailBox.setEnabled(editFlag)
        self.smileListBox.setEnabled(not editFlag)
        # setting movie
        self.movieLabel.clear()
        if icon and icon.image and os.path.exists(os.path.join(options.TEMP_DIR, icon.image)):
            self.movie = QtGui.QMovie(os.path.join(options.TEMP_DIR, icon.image))
            self.movieLabel.setMovie(self.movie)
            self.movieLabel.movie().start()
        # setting text
        self.textList.clear()
        self.textEdit.clear()
        if icon and icon.text:          
            self.textList.addItems(icon.text)
            self.textList.setCurrentRow(0)
            self.textEdit.setText(self.textList.currentItem().text())

    @pyqtSignature("")
    def on_actionExport_To_Kopete_triggered(self):
        targetFile = QtGui.QFileDialog.getSaveFileName(self, "Export to Kopete JISP", self.pack.name + ".jisp", "Kopete Smile Pack JISP (*.jisp)")
        if targetFile:
            exportKopete(self.pack, str(targetFile))
        
    @pyqtSignature("")
    def on_actionExport_To_Pidgin_triggered(self):
        targetFile = QtGui.QFileDialog.getSaveFileName(self, "Export to Pidgin ZIP", self.pack.name + "_pidgin.zip", "Pidgin Smile Pack ZIP (*.zip)")
        if targetFile:    
            exportPidgin(self.pack, str(targetFile))
        
    @pyqtSignature("")
    def on_actionExport_To_Qip_triggered(self):
        targetFile = QtGui.QFileDialog.getSaveFileName(self, "Export to QIP ZIP", self.pack.name + "_qip.zip", "QIP Smile Pack ZIP (*.zip)")
        if targetFile:
            exportQip(self.pack, str(targetFile))

    @pyqtSignature("")
    def on_actionExport_To_All_triggered(self):
        targetDir = QtGui.QFileDialog.getExistingDirectory(self, "Export to All", os.path.expanduser('~'))
        if targetDir:
            exportAll(self.pack, str(targetDir))
        
    @pyqtSignature("")
    def on_actionImport_From_Kopete_triggered(self):
        targetFile = QtGui.QFileDialog.getOpenFileName(self, "Import From Kopete JISP", os.path.expanduser('~'), "Kopete Smile Pack JISP (*.jisp)")
        if targetFile:
            self.pack = importKopete(str(targetFile))
            self.fillTable()

    @pyqtSignature("")
    def on_actionImport_From_Pidgin_ZIP_triggered(self):
        targetFile = QtGui.QFileDialog.getOpenFileName(self, "Import From Pidgin ZIP", os.path.expanduser('~'), "Pidgin Smile Pack ZIP (*.zip)")
        if targetFile:
            self.pack = importPidginZip(str(targetFile))
            self.fillTable()
            
    @pyqtSignature("")
    def on_actionImport_From_QIP_ZIP_triggered(self):
        targetFile = QtGui.QFileDialog.getOpenFileName(self, "Import From QIP ZIP", os.path.expanduser('~'), "QIP Smile Pack ZIP (*.zip)")
        if targetFile:
            self.pack = importQipZip(str(targetFile))
            self.fillTable()
