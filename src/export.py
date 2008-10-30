import os
from itertools import ifilter
from xml.dom import getDOMImplementation
from zipfile import ZipFile
import options
from util import printTiming

@printTiming
def exportPidgin(pack, targetFile):
    print "export to pidgin started..."
    content = ["Name=" + pack.name + "\n"]
    if pack.author:
        content.append("Author=" + pack.author + "\n")
    if pack.icon:
        content.append("Icon=" + pack.icon + "\n")
    content.append("[default]\n")
    for icon in pack.icons:
        # escaping '\'
        for i, text in enumerate(ifilter(lambda text: "\\" in text, icon.text)):
            # TODO simplify insertion
            temp = list(text)
            temp.insert(text.find("\\"), "\\")
            text = "".join(temp)
            # TODO may be bad
            icon.text[i] = text
        # escaping ' '
        for i, text in enumerate(ifilter(lambda text: " " in text, icon.text)):
            # TODO simplify insertion
            temp = list(text)
            temp.insert(text.find(" "), "\\")
            text = "".join(temp)
            # TODO may be bad
            icon.text[i] = text
        fullText = icon.image + " " + " ".join(icon.text) + "\n"
        content.append(fullText)
    zip = ZipFile(targetFile, "w")
    zip.writestr(os.path.join(pack.name, "theme"), "".join(content))
    for icon in pack.icons:
        zip.write(os.path.join(options.TEMP_DIR, icon.image), os.path.join(pack.name, icon.image))
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
    print "export to qip finished"

@printTiming    
def exportAll(pack, targetDir):
    exportKopete(pack, os.path.join(targetDir, pack.name + ".jisp"))
    exportPidgin(pack, os.path.join(targetDir, pack.name + "_pidgin.zip"))
    exportQip(pack, os.path.join(targetDir, pack.name + "_qip.zip"))
