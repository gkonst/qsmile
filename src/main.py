#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from PyQt4.QtGui import QApplication
from MainWindow import MainWindow


def main() :
    app = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()
