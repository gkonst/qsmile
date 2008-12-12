# -*- coding: utf-8 -*-
#
#    qsmile/core/importpack.py
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
from zipfile import ZipFile, is_zipfile
from qsmile.core.model import Pack,  Icon
import qsmile.core.config as config
from qsmile.core.util import timing, log

@timing
def import_kopete(target_file):
    log.debug("import from kopete jisp started...%s", target_file)
    try:
        content = _read_content_from_zip(target_file, "icondef.xml")
    except IOError, (errno, strerror):
        log.warn("import from kopete failed : %s", strerror)
        raise ImportPackError("Error during importing : " + strerror)
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
            log.debug(" pack name : %s",  pack.name)
    xml_icons = dom.getElementsByTagName("icon")
    for xml_icon in xml_icons:
        icon = Icon([], str(xml_icon.getElementsByTagName("object")[0].firstChild.data))
        for text in xml_icon.getElementsByTagName("text"):
            icon.add_text(str(text.firstChild.data))
        log.debug(" importing image : %s ", icon.image)
        try: 
            image_content = _read_content_from_zip(target_file, icon.image)
            fout = open(os.path.join(config.temp_dir, icon.image),  "wb")
            fout.write(image_content)
            fout.close()
        except IOError, (errno, strerror):
            log.warn("error during loading image : " + strerror + " -> skipping")            
        pack.add_icon(icon)
    log.debug("import from kopete jisp finished")
    return pack;

@timing
def import_pidgin_zip(target_file):
    log.debug("import from pidgin zip started...%s", target_file)
    pack =  _import_pidgin(target_file, _read_content_from_zip)
    log.debug("import from pidgin zip finished")
    return pack

@timing
def import_pidgin_dir(target_dir):
    log.debug("import from pidgin dir started...%s", target_dir)
    pack =  _import_pidgin(target_dir, _read_content_from_file)
    log.debug("import from pidgin dir finished")
    return pack
    
def _import_pidgin(target_path, read_function):
    try:
        content = read_function(target_path, "theme")
    except IOError, (errno, strerror):
        log.warn("import from pidgin failed : %s", strerror)
        raise ImportPackError("Error during importing : " + strerror)
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
            log.debug("  text : %s", icon.text)
            log.debug(" importing image : %s", icon.image)
            try:
                image_content = read_function(target_path, icon.image)
                fout = open(os.path.join(config.temp_dir, icon.image),  "wb")
                fout.write(image_content)
                fout.close()          
                pack.add_icon(icon)
            except IOError, (errno, strerror):
                log.warn("error during loading image : " + strerror + " -> skipping")
        elif "Name=" in line:
            pack.name = line.partition("=")[2].strip()
        elif "Author=" in line:
            pack.author = line.partition("=")[2].strip()
        elif "[default]" in line:
            smile_part_started = True
    return pack

@timing
def import_qip_zip(target_file):
    log.debug("import from qip zip started...%s", target_file)
    # TODO add validation
    zip_file = ZipFile(target_file, "r")
    define_entry = filter(lambda item: item.endswith("_define.ini"), zip_file.namelist())[0]
    content = zip_file.read(define_entry)
    pack = Pack()
    pack.name = define_entry.partition("/")[0]
    log.debug(" pack name : %s", pack.name)
    images = filter(lambda item: item.endswith(".gif"), zip_file.namelist())
    images.sort()
    for line, image_entry in zip(content.splitlines(), images):
        log.debug(" line : %s, image : %s", line, image_entry)
        icon = Icon(line.split(","), image_entry.rpartition("/")[2])
        log.debug(" text : %s, image : %s", icon.text, icon.image)
        log.debug(" importing image : %s, from entry : %s", icon.image, image_entry) 
        image_content = zip_file.read(image_entry)
        fout = open(os.path.join(config.temp_dir, icon.image),  "wb")
        fout.write(image_content)
        fout.close()
        pack.add_icon(icon)
    log.debug("import from qip zip finished") 
    return pack

@timing
def import_qip_dir(target_dir):
    log.debug("import from qip dir started...%s", target_dir)
    # TODO add validation
    pack_dir = os.path.join(target_dir, "Animated")
    pack = Pack()
    pack.name = pack_dir.rpartition(os.sep)[0].rpartition(os.sep)[2]
    log.debug(" pack name : %s", pack.name)
    content = _read_content_from_file(pack_dir, "_define.ini")
    images = filter(lambda item: item.endswith(".gif"), os.listdir(pack_dir))
    images.sort()
    for line, image_entry in zip(content.splitlines(), images):
        log.debug(" line : %s, image : %s", line, image_entry)
        icon = Icon(line.split(","), image_entry.rpartition(os.sep)[2])
        log.debug(" text : %s, image : %s", icon.text, icon.image)
        log.debug(" importing image : %s, from entry : %s", icon.image, image_entry) 
        image_content = _read_content_from_file(pack_dir, image_entry)
        fout = open(os.path.join(config.temp_dir, icon.image),  "wb")
        fout.write(image_content)
        fout.close()
        pack.add_icon(icon)
    log.debug("import from qip dir finished")
    return pack

def _read_content_from_file(dir, file):
    fin = open(os.path.join(dir, file))
    content = fin.read()
    fin.close()
    return content

def _read_content_from_zip(file, entry):
    if not is_zipfile(file):
        raise IOError(None, "Not a zip file format")
    zip_file = ZipFile(file, "r")
    try:
        content = zip_file.read(filter(lambda item: item.endswith(entry), zip_file.namelist())[0])
    except IndexError:
        raise IOError(None, "File entry not found in zip : " + entry)
    zip_file.close()
    return content

class ImportPackError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

