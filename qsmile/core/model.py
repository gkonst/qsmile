# -*- coding: utf-8 -*-
#
#    qsmile/core/model.py
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
Module contains model classes.
"""
class Icon(object):
    """
    Class represents smile.
    
    Contains image name and text smile definitions. 
    """
    def __init__(self, text, image=None):
        """
        Initializes icon instance with specific text and image (None by default).
        """
        self.text = text
        self.image = image

    def add_text(self, text):
        """
        Adds text element to current icon.
        """
        self.text.append(text)
        
    def __str__(self):
        """
        Returns image and text.
        """
        return "Icon(image=" + str(self.image) + ", text=" + str(self.text) + ")"
    
    def validate_icon(self):
        """
        Validates icon.
        
        Checks image and text for emptiness.
        """
        if not self.image:
            return False
        elif not self.text:
            return False
        else:
            return True
    
class Pack(object):
    """
    Class represents smile pack.
    
    Contains pack info and smileys. 
    """
    def __init__(self):
        self.icons = []
        self.author = "UNKNOWN"
        self.name = "UNKNOWN"
        self.icon = ""
        self.version = ""
        self.desc = ""
        self.created = ""
        
    def add_icon(self, icon):
        """
        Adds icon to pack.
        """
        self.icons.append(icon)
        
    def delete_icon(self, i):
        """
        Deletes icon form pack.
        """
        del self.icons[i]

    def generate_icon_filename(self):
        """
        Generates icon image filename.
        
        Image names is generated as sequence from characters, like 'aa', 'bb', etc.
        """
        if self.icons:
            temp = list(self.icons[-1].image[0:-4])
            if(ord(temp[1]) == 122):
                temp[0] = chr(ord(temp[0]) + 1)
            else:
                temp[1] = chr(ord(temp[1]) + 1)
            return "".join(temp) + ".gif"
        else:
            return "aa.gif"
