# -*- coding: utf-8 -*-
#
#    src/common.py
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
Module contains common functionality classes.
"""
class ModeForm(object):
    """
    Class incapsulates mode operations for form.
    """
    def __init__(self):
        self.mode = None
        
    def isEditMode(self):
        return self.mode == "edit"
    
    def isViewMode(self):
        return self.mode == "view"
    
    def isCreateMode(self):
        return self.mode == "create"
    
    def setCreateMode(self):
        self.mode = "create"

    def setEditMode(self):
        self.mode = "edit"

    def setViewMode(self):
        self.mode = "view"