"""
DUI2's bindings for Qt library

Author: Luis Fuentes-Montero (Luiso)
With strong help from DIALS and CCP4 teams

copyright (c) CCP4 - DLS
"""

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import sys

def is_webengine_functional(pyside_ver):
    # 1. Check if module is even importable
    try:
        if pyside_ver == 6:
            from PySide6 import QtWebEngineWidgets

        else:
            #assuming pyside_ver = 2
            from PySide2 import QtWebEngineWidgets

    except ImportError:
        print("Here fail #1")
        return False

    # 2. Locate the helper executable
    # Qt searches for this file to render web content
    #process_path = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.LibraryExecutablesPath)
    process_path = QLibraryInfo.location(QLibraryInfo.LibraryExecutablesPath)
    print("process_path =", process_path)
    if sys.platform == "win32":
        filename = "QtWebEngineProcess.exe"

    else:
        filename = "QtWebEngineProcess"

    #filename = "QtWebEngineProcess.exe" if sys.platform == "win32" else "QtWebEngineProcess"
    full_path = os.path.join(process_path, filename)

    if not os.path.exists(full_path):
        # Path might be different in virtualenvs or bundled apps
        # fallback check in standard QtWebEngineWidgets path
        full_path = os.path.join(
            os.path.dirname(QtWebEngineWidgets.__file__), "Qt", "bin", filename
        )

    if not os.path.exists(full_path):
        print("Here fail #2")
        return False

    print("Here YES")
    return True


pyside_ver = 6

try:
    from PySide6 import QtUiTools
    from PySide6.QtCore import *
    from PySide6.QtWidgets import *
    from PySide6.QtGui import *
    print("Using PySide6 as Qt bindings")
    if is_webengine_functional(pyside_ver):
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtWebEngineCore import QWebEngineSettings

        except (ImportError, ModuleNotFoundError):
            print(
                " Web Engine module not found, working with system web browser "
            )

except (ImportError, ModuleNotFoundError):
    pyside_ver = 2
    from PySide2 import QtUiTools
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    print("Using PySide2 as Qt bindings")
    if is_webengine_functional(pyside_ver):
        try:
            from PySide2.QtWebEngineWidgets import (
                QWebEngineView, QWebEngineSettings
            )

        except (ImportError, ModuleNotFoundError):
            print(
                " Web Engine module not found, working with system web browser "
            )
