# -*- coding: utf-8 -*-
#
#    qsmile/core/util.py
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
Module contains various utility methods.
"""
import time
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)-1s] %(asctime)s %(module)s:%(funcName)s:%(lineno)d - %(message)s"
)
log = logging.getLogger("qsmile") 

def timing(func):
    def timing(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        log.debug("*** %s took %0.3f s or %0.3f ms" % (func.func_name, (t2 - t1), (t2 - t1) * 1000.0))
        return res
    return timing
