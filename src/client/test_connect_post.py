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

import sys, json, logging
import requests

uni_url = 'http://127.0.0.1:45678/'
#uni_url = 'http://127.0.0.1:45679/'
#uni_url = 'http://supercomputo.cimav.edu.mx:45678/'


if __name__ == "__main__":

        full_cmd = {'nod_lst': [48], 'cmd_lst': ['split_node']}
        new_tst = '''
        full_cmd = {
            'nod_lst': [0],
            'cmd_lst': [
                'dials.import input.template="/home/luiso/dif_dat/C2sum_5/C2sum_5_####.cbf.gz"'
            ]
        }
        '''

        req_post = requests.post(uni_url, stream = True, data = full_cmd)
        while True:
            tmp_dat = req_post.raw.readline()
            print("tmp_dat =", tmp_dat)
            #tmp_dat = req_post.raw.readline()
            line_str = str(tmp_dat.decode('utf-8'))

            if '/*EOF*/' in line_str:
                print('/*EOF*/ received')
                break

            else:
                print(str(line_str[:-1]))

