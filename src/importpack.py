# -*- coding: utf-8 -*-
#
#    src/importpack.py
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
Module contains various import methods.
"""
import os
from itertools import ifilter
from zipfile import ZipFile
from model import Pack,  Icon
import options
from util import printTiming

@printTiming
def importKopete(targetFile):
    print "import from kopete jisp started..."
    zip = ZipFile(targetFile, "r")
    content = zip.read(filter(lambda item: item.endswith("icondef.xml"), zip.namelist())[0])
    pack = Pack()
    try:
        from xml.dom.ext.reader import PyExpat
        dom = PyExpat.Reader().fromString(content)
    except ImportError:
        from xml.dom.minidom import parseString
        dom = parseString(content)
    xmlMeta = dom.getElementsByTagName("meta")
    if xmlMeta:
        xmlName = xmlMeta[0].getElementsByTagName("name")
        if xmlName:
            pack.name = str(xmlName[0].firstChild.data)
            print " pack name : ",  pack.name
    xmlIcons = dom.getElementsByTagName("icon")
    for xmlIicon in xmlIcons:
        icon = Icon([], str(xmlIicon.getElementsByTagName("object")[0].firstChild.data))
        pack.addIcon(icon)
        for text in xmlIicon.getElementsByTagName("text"):
            icon.addText(str(text.firstChild.data))
            #print text.firstChild.data
    for icon in pack.icons:
        imageEntry = filter(lambda item: item.endswith(icon.image), zip.namelist())[0]
        print " importing image : ", icon.image, " from entry : ", imageEntry 
        imageContent = zip.read(imageEntry)
        fout = open(os.path.join(options.TEMP_DIR, icon.image),  "wb")
        fout.write(imageContent)
        fout.close()
    return pack;
    print "import from kopete jisp finished"

@printTiming
def importPidginZip(targetFile):
    print "import from pidgin zip started..."
    zip = ZipFile(targetFile, "r")
    content = zip.read(filter(lambda item: item.endswith("theme"), zip.namelist())[0])
    pack = Pack()
    smilePartStarted = False
    for line in ifilter(lambda line: line and not line.startswith("!"), content.split("\n")):
        line = line.replace("\t", " ")
        if smilePartStarted:
            icon = Icon([], line.partition(" ")[0])
            texts = line.partition(" ")[2].strip().split(" ")
            print "  texts : ", texts
            i = 0
            while i < len(texts):
                text = ""
                if texts[i].endswith("\\") and not texts[i].endswith("\\\\"):
                    # merge texts with '\ '
                    text = texts[i].replace("\\", "") + " " + texts[i + 1]
                    i += 2
                else:
                    text = texts[i]
                    i += 1
                icon.addText(text.replace("\\\\", "\\"))
            print "  text : ", icon.text
            pack.addIcon(icon)
            print " importing image : ", icon.image
            print zip.namelist()
            imageEntry = filter(lambda item: item.endswith(icon.image), zip.namelist())[0]
            print " from entry : ", imageEntry 
            imageContent = zip.read(imageEntry)
            fout = open(os.path.join(options.TEMP_DIR, icon.image),  "wb")
            fout.write(imageContent)
            fout.close()          
        elif "Name=" in line:
            pack.name = line.partition("=")[2].strip()
        elif "Author=" in line:
            pack.author = line.partition("=")[2].strip()
        elif "[default]" in line:
            smilePartStarted = True
    return pack
    print "import from pidgin zip finished"
    
@printTiming
def importQipZip(targetFile):
    print "import from qip zip started..."
    zipFile = ZipFile(targetFile, "r")
    defineEntry = filter(lambda item: item.endswith("_define.ini"), zipFile.namelist())[0]
    content = zipFile.read(defineEntry)
    pack = Pack()
    pack.name = defineEntry.partition(os.sep)[0]
    images = filter(lambda item: item.endswith(".gif"), zipFile.namelist())
    images.sort()
    for line, imageEntry in zip(content.split("\n"), images):
        print " line : ", line, " image : ", imageEntry
        icon = Icon(line.split(","), imageEntry.rpartition(os.sep)[2])
        print " text : ", icon.text, " image : ", icon.image
        print " importing image : ", icon.image, " from entry : ", imageEntry 
        imageContent = zipFile.read(imageEntry)
        fout = open(os.path.join(options.TEMP_DIR, icon.image),  "wb")
        fout.write(imageContent)
        fout.close()
        pack.addIcon(icon) 
    return pack
    print "import from qip zip finished"
