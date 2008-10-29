
from xml.dom.minidom import parse
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import PyExpat
import os
from model import Pack,  Icon
from export import createKopeteXML
import options
from util import printTiming

class DAO(object):
    @printTiming
    def loadPack(self):
        print "loading pack..."
        pack = Pack()
        dom = PyExpat.Reader().fromStream(open(os.path.join(options.TEMP_DIR, "icondef.xml"), "r"))
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
        print "pack loaded"
        return pack

    @printTiming
    def updatePack(self, pack):
        print "updating pack..."   
        packDocument = createKopeteXML(pack)
        fout = open(os.path.join(options.TEMP_DIR, "icondef.xml"),  "w")
        if not options.PRETTY_XML:
            packDocument.writexml(fout)
        else:
            #fout.write(packDocument.toprettyxml())
            PrettyPrint(packDocument, fout)
        fout.close()
        print "pack updated"