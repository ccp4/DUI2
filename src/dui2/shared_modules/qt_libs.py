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

try:
    from PySide6 import QtUiTools
    from PySide6.QtCore import *
    from PySide6.QtWidgets import *
    from PySide6.QtGui import *
    print("Using PySide6 as Qt bindings")
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtWebEngineCore import QWebEngineSettings

    except (ImportError, ModuleNotFoundError):
        print(
            " Web Engine module not found, working with system web browser "
        )

except (ImportError, ModuleNotFoundError):

    from PySide2 import QtUiTools
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    print("Using PySide2 as Qt bindings")

    try:
        from PySide2.QtWebEngineWidgets import (
            QWebEngineView, QWebEngineSettings
        )

    except (ImportError, ModuleNotFoundError):
        print(
            " Web Engine module not found, working with system web browser "
        )

should_be_imported_like_this = '''
from dui2.shared_modules.qt_libs import *
'''
