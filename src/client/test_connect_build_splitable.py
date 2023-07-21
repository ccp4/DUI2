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

def requests_post(cmd_in):
    req_post = requests.post(uni_url, stream = True, data = cmd_in)
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


if __name__ == "__main__":
    tree_size = 5
    for n in range(tree_size):
        import_cmd = 'dials.import '
        #imgs_path = 'input.template="/home/luiso/dif_dat/C2sum_5/C2sum_5_'
        #imgs_path = 'input.template="/home/lui/diff_data/C2sum_1/C2sum_1_'
        imgs_path = 'input.template="/home/lui/dif_dat/x4_wide/X4_wide_M1S4_2_'
        str_num = "{:3}".format(n) + "#"
        str_num = str_num.replace(" ", "0")

        #imgs_path += str_num + '.cbf.gz"'
        imgs_path += str_num + '.cbf"'
        import_cmd += imgs_path
        full_cmd = {'nod_lst': [0], 'cmd_lst': [import_cmd]}
        requests_post(full_cmd)

    for n in range(tree_size):
        n1 = n+1
        full_cmd = {'nod_lst': [n1], 'cmd_lst': ['dials.find_spots']}
        requests_post(full_cmd)


    for n in range(tree_size):
        n1 = n + tree_size + 1
        full_cmd = {'nod_lst': [n1], 'cmd_lst': ['dials.index']}
        requests_post(full_cmd)

    lst_par_nod = []
    for n in range(tree_size):
        n1 = n + tree_size * 2 + 1
        lst_par_nod.append(n1)
        nxt_nod = n1 + 1

    full_cmd = {'nod_lst': lst_par_nod, 'cmd_lst': ['dials.combine_experiments']}
    requests_post(full_cmd)
    '''
    full_cmd = {'nod_lst': [nxt_nod], 'cmd_lst': ['dials.split_experiments']}
    requests_post(full_cmd)
    '''


