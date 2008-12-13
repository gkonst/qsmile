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

import ez_setup
ez_setup.use_setuptools()

import os
import sys
import subprocess
from distutils import cmd
from distutils.command.build import build as _build
from setuptools import setup, find_packages

try:
    import py2exe
except ImportError:
    print "WARNING: you don't have py2exe installed, so .exe creation disabled"

try:
    import PyQt4
except ImportError:
    print "ERROR: PyQt not found! Please install it before running install."
    sys.exit(-1)

def _generate_manifest_in():
    """
    Generates 'MANIFEST.in' for sdist command.
    
    Manifest file includes images dir.
    """
    if os.path.exists("MANIFEST.in"):
        os.remove("MANIFEST.in")
    fin = open("MANIFEST.in", "wt")
    fin.write("include qsmile/ui/images/*.*")
    fin.close()

_generate_manifest_in()

class pyuic(cmd.Command):
    description = "Generates .py from .ui"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.path.walk(".", self._process, None)
        
    def _process(self, arg, dirname, names):
        files = filter(lambda param: param[-3:] == '.ui' , names)
        for ui in files:
            target_name = os.path.join(dirname, "Ui_" + ui[0: -3] + ".py")
            print "processing ", os.path.join(dirname, ui), " -> ", target_name
            try:
                subprocess.call(["pyuic4", os.path.join(dirname, ui), "-o",target_name])
            except OSError, (errno, strerror):
                print "ERROR: can't run pyuic4 - ", strerror
                sys.exit(-1)
                
class pyrcc(cmd.Command):
    description = "Generates .py from .rc"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.path.walk(".", self._process, None)
        
    def _process(self, arg, dirname, names):
        files = filter(lambda param: param[-4:] == '.qrc' , names)
        for rc in files:
            target_name = os.path.join(dirname, rc[0: -4] + "_rc.py")
            print "processing ", os.path.join(dirname, rc), " -> ", target_name
            try:
                subprocess.call(["pyrcc4", os.path.join(dirname, rc), "-o",target_name])
            except OSError, (errno, strerror):
                print "ERROR: can't run pyrcc4 - ", strerror
                sys.exit(-1)

class build(_build):
    sub_commands = [('pyuic', None), ('pyrcc', None)] + _build.sub_commands
    def run(self):
        _build.run(self)

cmdclass = {
    'build': build,
    'pyuic': pyuic,
    'pyrcc': pyrcc,
}

setup(
    name = "qsmile", 
    version = "0.3_pre",
    author =  "Konstantin Grigoriev",
    author_email = "Konstantin.V.Grigoriev@gmail.com",
    url = "http://code.google.com/p/qsmile/",
    license = "GPLv3",
    cmdclass = cmdclass,
    packages = find_packages(),
    include_package_data = True,
    package_data = {"qsmile.ui" : ["images/*.*"]},
    entry_points = """
        [console_scripts]
            qsmile = qsmile.main:start_ui
    """,
    options = {"py2exe": {
                    "bundle_files": 1,
                    "includes": ["sip", "qsmile.ui.mainwindow"]}}, 
    windows = ["qsmile_runner.py"]
)
