# -*- coding: utf-8 -*-
import os
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
        imageContent = zip.read("%(dir)s/%(image)s" % {"dir" : pack.name, "image" : icon.image})
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
    for line in content.split("\n"):
        if smilePackStarted:
            icon = Icon([], line.partition(" ")[0])
            #TODO implement text processing
            pack.addIcon(icon)
        elif "Name=" in line:
            pack.name = line.partition("=")[2]
        elif "Author=" in line:
            pack.author = line.partition("=")[2]
        elif "[default]" in line:
            smilePartStarted = True
    return pack
    print "import from pidgin zip finished"
    
@printTiming
def importQipZip(targetFile):
    print "import from qip zip started..."
    zip = ZipFile(targetFile, "r")
    content = zip.read(filter(lambda item: item.endswith("_define.ini"), zip.namelist())[0])
    pack = Pack()
    
    return pack
    print "import from qip zip finished"
