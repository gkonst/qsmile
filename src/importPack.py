from zipfile import ZipFile
from xml.dom.ext.reader import PyExpat
import os
from model import Pack,  Icon
#from dao import DAO
import options
from util import printTiming

@printTiming
def importKopete(targetFile):
    print "import from kopete jisp started..."
    zip = ZipFile(targetFile, "r")
    content = zip.read(filter(lambda item: item.endswith("icondef.xml"), zip.namelist())[0])
    pack = Pack()
    dom = PyExpat.Reader().fromString(content)
    xmlMeta = dom.getElementsByTagName("meta")
    if xmlMeta:
        xmlName = xmlMeta[0].getElementsByTagName("name")
        if xmlName:
            pack.name = str(xmlName[0].firstChild.data)
    xmlIcons = dom.getElementsByTagName("icon")
    for xmlIicon in xmlIcons:
        icon = Icon([], str(xmlIicon.getElementsByTagName("object")[0].firstChild.data))
        pack.addIcon(icon)
        for text in xmlIicon.getElementsByTagName("text"):
            icon.addText(str(text.firstChild.data))
            #print text.firstChild.data
    for icon in pack.icons:
        imageContent = zip.read(os.path.join(pack.name, icon.image))
        fout = open(os.path.join(options.TEMP_DIR, icon.image),  "wb")
        fout.write(imageContent)
        fout.close()
#    DAO().updatePack(pack)
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
        elif line.find("Name=") != -1:
            pack.name = line.partition("=")[2]
        elif line.find("Author=") != -1:
            pack.author = line.partition("=")[2]
        elif line.find("[default]"):
            smilePartStarted = True
    return pack
    print "import from pidgin zip finished"