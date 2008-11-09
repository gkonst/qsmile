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
from util import timing

@timing
def import_kopete(target_file):
    print "import from kopete jisp started..."
    zip_file = ZipFile(target_file, "r")
    content = zip_file.read(filter(lambda item: item.endswith("icondef.xml"), zip_file.namelist())[0])
    pack = Pack()
    try:
        from xml.dom.ext.reader import PyExpat
        dom = PyExpat.Reader().fromString(content)
    except ImportError:
        from xml.dom.minidom import parseString
        dom = parseString(content)
    xml_meta = dom.getElementsByTagName("meta")
    if xml_meta:
        xml_name = xml_meta[0].getElementsByTagName("name")
        if xml_name:
            pack.name = str(xml_name[0].firstChild.data)
            print " pack name : ",  pack.name
    xml_icons = dom.getElementsByTagName("icon")
    for xml_icon in xml_icons:
        icon = Icon([], str(xml_icon.getElementsByTagName("object")[0].firstChild.data))
        pack.add_icon(icon)
        for text in xml_icon.getElementsByTagName("text"):
            icon.add_text(str(text.firstChild.data))
            #print text.firstChild.data
    for icon in pack.icons:
        image_entry = filter(lambda item: item.endswith(icon.image), zip_file.namelist())[0]
        print " importing image : ", icon.image, " from entry : ", image_entry 
        image_content = zip_file.read(image_entry)
        fout = open(os.path.join(options.TEMP_DIR, icon.image),  "wb")
        fout.write(image_content)
        fout.close()
    return pack;
    print "import from kopete jisp finished"

@timing
def import_pidgin_zip(target_file):
    print "import from pidgin zip started..."
    pack =  _import_pidgin(target_file, _read_content_from_zip)
    print "import from pidgin zip finished"
    return pack

@timing
def import_pidgin_folder(target_dir):
    print "import from pidgin folder started..."
    pack =  _import_pidgin(target_dir, _read_content_from_file)
    print "import from pidgin folder finished"
    return pack
    
def _import_pidgin(target_path, read_function):
    content = read_function(target_path, "theme")
    pack = Pack()
    smile_part_started = False
    for line in ifilter(lambda line: line and not line.startswith("!"), content.split("\n")):
        line = line.replace("\t", " ")
        if smile_part_started:
            icon = Icon([], line.partition(" ")[0])
            texts = line.partition(" ")[2].strip().split(" ")
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
                icon.add_text(text.replace("\\\\", "\\"))
            print "  text : ", icon.text
            pack.add_icon(icon)
            print " importing image : ", icon.image
            image_content = read_function(target_path, icon.image)
            fout = open(os.path.join(options.TEMP_DIR, icon.image),  "wb")
            fout.write(image_content)
            fout.close()          
        elif "Name=" in line:
            pack.name = line.partition("=")[2].strip()
        elif "Author=" in line:
            pack.author = line.partition("=")[2].strip()
        elif "[default]" in line:
            smile_part_started = True
    return pack

@timing
def import_qip_zip(target_file):
    print "import from qip zip started..."
    zip_file = ZipFile(target_file, "r")
    define_entry = filter(lambda item: item.endswith("_define.ini"), zip_file.namelist())[0]
    content = zip_file.read(define_entry)
    pack = Pack()
    pack.name = define_entry.partition("/")[0]
    images = filter(lambda item: item.endswith(".gif"), zip_file.namelist())
    images.sort()
    for line, image_entry in zip_file(content.split("\n"), images):
        print " line : ", line, " image : ", image_entry
        icon = Icon(line.split(","), image_entry.rpartition("/")[2])
        print " text : ", icon.text, " image : ", icon.image
        print " importing image : ", icon.image, " from entry : ", image_entry 
        image_content = zip_file.read(image_entry)
        fout = open(os.path.join(options.TEMP_DIR, icon.image),  "wb")
        fout.write(image_content)
        fout.close()
        pack.add_icon(icon) 
    return pack
    print "import from qip zip finished"

def _read_content_from_file(dir, file):
    fin = open(os.path.join(dir, file))
    content = fin.read()
    fin.close()
    return content

def _read_content_from_zip(file, entry):
    zip_file = ZipFile(file, "r")
    content = zip_file.read(filter(lambda item: item.endswith(entry), zip_file.namelist())[0])
    zip_file.close()
    return content
