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

import sys, time, logging, os, platform

from dui2.shared_modules.qt_libs import *

from dui2.client.q_object import MainObject
from dui2.client.init_firts import ini_data
from dui2.client.exec_utils import get_req_json_dat

from dui2.shared_modules import format_utils

def main(par_def = None):
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"
    if platform.system() == "Windows":
        print("Running on Windows")

    else:
        print("Running on Unix-like O.S.")
        os.environ["QT_QPA_PLATFORM"] = "xcb"
        os.environ["WAYLAND_DISPLAY"] = ""

    data_init = ini_data()
    data_init.set_data(par_def)
    uni_url = str(data_init.get_url())

    token_from_cli = data_init.get_token()
    print("token(client side)=", token_from_cli)

    tmp_dat_dir = format_utils.create_tmp_dir()
    logging.info("creating " + str(tmp_dat_dir) + "for temporary files")

    data_init.set_tmp_dir(tmp_dat_dir)

    logging.info(
        'get_if_local =' + str(data_init.get_if_local()) + 'get_url =' + uni_url
    )
    cmd = {"nod_lst":[""], "cmd_str":["display"]}
    dummy_nod_lst = None
    n_secs = 3
    while dummy_nod_lst == None:
        logging.info("here in loop")
        lst_req = get_req_json_dat(params_in = cmd, main_handler = None)
        dummy_nod_lst = lst_req.result_out()
        if dummy_nod_lst == None:
            time.sleep(n_secs)

        else:
            logging.info("dummy_nod_lst != None ...\n launching GUI")

    app = QApplication(sys.argv)
    m_obj = MainObject(parent = app)
    sys.exit(app.exec_())

