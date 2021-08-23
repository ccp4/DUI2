"""
DUI2's server connecting test

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

import sys, json
import requests

lst_cmd = [
             {"nod_lst":[1], "cmd_lst":"gis " +
              str(0) + " view_rect=" +
              str(500) + "," + str(500) + "," +
              str(5555) + "," + str(500)}
          ,
             {"nod_lst":[1], "cmd_lst":"gis " +
              str(0) + " view_rect=" +
              str(500) + "," + str(500) + "," +
              str(55) + "," + str(5000)}

          ,
             {"nod_lst":[1], "cmd_lst":"gis " +
              str(0) + " view_rect=" +
              str(50550) + "," + str(500) + "," +
              str(555) + "," + str(50)}
          ,
             {"nod_lst":[1], "cmd_lst":"gis " +
              str(0) + " view_rect=" +
              str(500) + "," + str(50550) + "," +
              str(555) + "," + str(500)}
          ,
             {"nod_lst":[1], "cmd_lst":"gis " +
              str(0) + " view_rect=" +
              str(-500) + "," + str(500) + "," +
              str(555) + "," + str(500)}

          ,
             {"nod_lst":[1], "cmd_list":"gis " +
              str(0) + " view_rect=" +
              str(-500) + "," + str(500) + "," +
              str(555) + "," + str(500)}

]

if __name__ == "__main__":
    for cmd in lst_cmd:
        for do_this in [{"nod_lst":[""], "cmd_lst":["d"]}, None]:
            if do_this == None:
                my_cmd = cmd

            else:
                my_cmd = do_this

            req_get = requests.get(
                'http://localhost:8765/', stream = True, params = my_cmd
            )

            while True:
                tmp_dat = req_get.raw.readline()
                line_str = str(tmp_dat.decode('utf-8'))

                if line_str[-7:] == '/*EOF*/':
                    print('/*EOF*/ received')
                    break

                else:
                    print(line_str[:-1])

