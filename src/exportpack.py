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
import config
from util import timing, log

@timing
def export_pidgin(pack, target_file):
    log.debug("export to pidgin started...%s", target_file)
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
        full_text = icon.image + " " + " ".join(icon.text) + "\n"
        content.append(full_text)
    zip_file = ZipFile(target_file, "w")
    zip_file.writestr(os.path.join(pack.name, "theme"), "".join(content))
    for icon in pack.icons:
        zip_file.write(os.path.join(config.temp_dir, icon.image), os.path.join(pack.name, icon.image))
    zip_file.close()
    log.debug("export to pidgin finished")
    
@timing
def export_kopete(pack, target_file):
    log.debug("export to kopete started...%s", target_file)
    pack_document = getDOMImplementation(config.dom_impl).createDocument(None, "icondef", None)
    meta_element = pack_document.createElement("meta")
    if pack.name:
        name_element = pack_document.createElement("name")
        name_element.appendChild(pack_document.createTextNode(pack.name))
        meta_element.appendChild(name_element)
    pack_document.documentElement.appendChild(meta_element)
    for icon in pack.icons:
        icon_element = pack_document.createElement("icon")
        image_element = pack_document.createElement("object")
        image_element.setAttribute("mime", "image/gif")
        icon_element.appendChild(image_element)
        image_text = pack_document.createTextNode(icon.image)
        image_element.appendChild(image_text)
        for text in icon.text:
            text_element = pack_document.createElement("text")
            icon_element.appendChild(text_element)
            text_text = pack_document.createTextNode(text)
            text_element.appendChild(text_text)
        pack_document.documentElement.appendChild(icon_element)
    content = ""
    try:
        import cStringIO as StringIO
        stream=StringIO.StringIO()
        from xml.dom.ext import PrettyPrint
        PrettyPrint(pack_document, stream)
        content = stream.getvalue()
    except ImportError:
        content = pack_document.toxml()
    zip_file = ZipFile(target_file, "w")
    zip_file.writestr(os.path.join(pack.name, "icondef.xml"), content)
    for icon in pack.icons:
        zip_file.write(os.path.join(config.temp_dir, icon.image), os.path.join(pack.name, icon.image))
    zip_file.close()
    log.debug("export to kopete finished")

@timing
def export_qip(pack, target_file):
    log.debug("export to qip started...%s", target_file)
    content = []
    for icon in pack.icons:
        content.append(",".join(icon.text) + "\n")
    zip_file = ZipFile(target_file, "w")
    zip_file.writestr(os.path.join(pack.name, "Animated", "_define.ini"), "".join(content))
    for icon in pack.icons:
        zip_file.write(os.path.join(config.temp_dir, icon.image), os.path.join(pack.name, "Animated", icon.image))
    zip_file.close()
    log.debug("export to qip finished")

@timing    
def export_all(pack, target_dir):
    export_kopete(pack, os.path.join(target_dir, pack.name + ".jisp"))
    export_pidgin(pack, os.path.join(target_dir, pack.name + "_pidgin.zip"))
    export_qip(pack, os.path.join(target_dir, pack.name + "_qip.zip"))
