"""
DUI2's Main function, client side

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

import sys, time

from PySide2.QtCore import *
from PySide2.QtWidgets import *

from q_object import MainObject
from init_firts import ini_data
from exec_utils import json_data_request

def main():
    data_init = ini_data()
    data_init.set_data()
    uni_url = data_init.get_url()
    cmd = {"nod_lst":[""], "cmd_lst":["display"]}
    dummy_nod_lst = None
    n_secs = 3
    while dummy_nod_lst == None:
        dummy_nod_lst = json_data_request(uni_url, cmd)
        if dummy_nod_lst == None:
            print("dummy_nod_lst =", dummy_nod_lst, ", waiting", n_secs, "secs ...")
            time.sleep(n_secs)

        else:
            print("dummy_nod_lst != None ...\n launching GUI")

    #QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    m_obj = MainObject(parent = app)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

