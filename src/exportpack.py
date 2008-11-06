# -*- coding: utf-8 -*-
#
#    src/exportpack.py
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
Module contains various export methods.
"""
import os
from itertools import ifilter
from xml.dom import getDOMImplementation
from zipfile import ZipFile
import options
from util import printTiming

@printTiming
def exportPidgin(pack, targetFile):
    print "export to pidgin started..."
    content = ["Name=%s\n"  % pack.name]
    if pack.author:
        content.append("Author=%s\n" % pack.author)
    if pack.icon:
        content.append("Icon=%s\n" % pack.icon)
    content.append("[default]\n")
    for icon in pack.icons:
        # escaping '\'
        for i, text in enumerate(ifilter(lambda text: "\\" in text, icon.text)):
            icon.text[i] = text.replace("\\", "\\\\")
        # escaping ' '
        for i, text in enumerate(ifilter(lambda text: " " in text, icon.text)):
            # TODO may be bad
            icon.text[i] = text.replace(" ","\\ ")
        fullText = icon.image + " " + " ".join(icon.text) + "\n"
        content.append(fullText)
    zip = ZipFile(targetFile, "w")
    zip.writestr(os.path.join(pack.name, "theme"), "".join(content))
    for icon in pack.icons:
        zip.write(os.path.join(options.TEMP_DIR, icon.image), os.path.join(pack.name, icon.image))
    zip.close()
    print "export to pidgin finished"
    
@printTiming
def exportKopete(pack, targetFile):
    print "export to kopete started..."
    packDocument = createKopeteXML(pack)
    content = ""
    if not options.PRETTY_XML:
        content = packDocument.toxml()
    else:
        import cStringIO as StringIO
        stream=StringIO.StringIO()
        from xml.dom.ext import PrettyPrint
        PrettyPrint(packDocument, stream)
        content = stream.getvalue()
    zip = ZipFile(targetFile, "w")
    zip.writestr(os.path.join(pack.name, "icondef.xml"), content)
    for icon in pack.icons:
        zip.write(os.path.join(options.TEMP_DIR, icon.image), os.path.join(pack.name, icon.image))
    zip.close()
    print "export to kopete finished"

def createKopeteXML(pack):
    impl = getDOMImplementation(options.DOM_IMPL)
    packDocument = impl.createDocument(None, "icondef", None)
    metaElement = packDocument.createElement("meta")
    if pack.name:
        nameElement = packDocument.createElement("name")
        nameElement.appendChild(packDocument.createTextNode(pack.name))
        metaElement.appendChild(nameElement)
    packDocument.documentElement.appendChild(metaElement)
    for icon in pack.icons:
        iconElement = packDocument.createElement("icon")
        imageElement = packDocument.createElement("object")
        imageElement.setAttribute("mime", "image/gif")
        iconElement.appendChild(imageElement)
        imageText = packDocument.createTextNode(icon.image)
        imageElement.appendChild(imageText)
        for text in icon.text:
            textElement = packDocument.createElement("text")
            iconElement.appendChild(textElement)
            textText = packDocument.createTextNode(text)
            textElement.appendChild(textText)
        packDocument.documentElement.appendChild(iconElement)
    return packDocument

@printTiming
def exportQip(pack, targetFile):
    print "export to qip started..."
    content = []
    for icon in pack.icons:
        content.append(",".join(icon.text) + "\n")
    zip = ZipFile(targetFile, "w")
    zip.writestr(os.path.join(pack.name, "Animated", "_define.ini"), "".join(content))
    for icon in pack.icons:
        zip.write(os.path.join(options.TEMP_DIR, icon.image), os.path.join(pack.name, "Animated", icon.image))
    zip.close()
    print "export to qip finished"

@printTiming    
def exportAll(pack, targetDir):
    exportKopete(pack, os.path.join(targetDir, pack.name + ".jisp"))
    exportPidgin(pack, os.path.join(targetDir, pack.name + "_pidgin.zip"))
    exportQip(pack, os.path.join(targetDir, pack.name + "_qip.zip"))
