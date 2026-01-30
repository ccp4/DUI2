"""
DUI2's client's side global initialization flags

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


import os, sys, logging
from dui2.shared_modules import format_utils

class IniData(object):
    def __init__(self):
        logging.info("IniData.__init__()")

    def set_data(self, par_def = None):
        if par_def == None:
            par_def = (
                ("url", 'http://127.0.0.1:45678/'),
                ("import_init", None),
                ("all_local", "False"),
                ("windows_exe", "False"),
            )

        init_param = format_utils.get_par(par_def, sys.argv[1:])
        logging.info("init_param =" + str(init_param))
        global uni_url
        try:
            uni_url = init_param["url"]

        except KeyError:
            uni_url = None

        logging.info("URL(client side) = " + str(uni_url))

        global token
        token = init_param["token"]

        global run_local
        try:
            if init_param["all_local"].lower() == "true":
                run_local = True

            else:
                run_local = False

        except KeyError:
            run_local = True

        logging.info("run_local(client) =" + str(run_local))

        global imp_ini_templ
        try:
            imp_ini_templ = init_param["import_init"]

        except KeyError:
            imp_ini_templ = None

        logging.info("imp_ini_templ(client) =" + str(imp_ini_templ))

        global win_exe
        if init_param["windows_exe"].lower() == "true":
            win_exe = True

        else:
            win_exe = False

        logging.info("\n win_exe =" + str(win_exe))

    def set_tmp_dir(self, dir_path_in):
        global tmp_dir
        tmp_dir = dir_path_in

    def get_if_local(self):
        return run_local

    def get_import_init(self):
        return imp_ini_templ

    def get_url(self):
        return uni_url

    def get_token(self):
        return token

    def get_tmp_dir(self):
        return tmp_dir

    def get_win_exe(self):
        return win_exe


if __name__ == "__main__":
    init_firts = IniData()
    logging.info("IniData.uni_url =" + str(init_firts.get_url()))

