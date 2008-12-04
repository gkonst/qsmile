# -*- coding: utf-8 -*-
#
#    setup.py
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
Module used for installing/uninstalling application.
"""

from setuptools import setup, find_packages
import os

def _generate_manifest_in():
    """
    Generates 'MANIFEST.in' for sdist command.
    
    Manifest file includes images dir.
    """
    if os.path.exists("MANIFEST.in"):
        os.remove("MANIFEST.in")
    fin = open("MANIFEST.in", "wt")
    fin.write("include src/ui/images/*.*")
    fin.close()

_generate_manifest_in()

setup(
      name = "qsmile", 
      version = "0.2",
      author =  "Konstantin Grigoriev",
      author_email = "Konstantin.V.Grigoriev@gmail.com",
      url = "http://code.google.com/p/qsmile/",
      license = "GPLv3",
      packages = find_packages(),
      include_package_data = True,
      package_data = {"src.ui" : ["images/*.*"]},
      entry_points = """
        [console_scripts]
            qsmile = src.qsmile:main
    """,
)
