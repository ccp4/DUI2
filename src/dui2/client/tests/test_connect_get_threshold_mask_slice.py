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

import sys, zlib
import requests
import numpy as np

uni_url = 'http://127.0.0.1:45678/'
#uni_url = 'http://127.0.0.1:45679/'
#uni_url = 'http://supercomputo.cimav.edu.mx:45678/'

if __name__ == "__main__":
    img_num = 0
    print("\n\n img_num =", img_num)
    full_cmd = {
        'nod_lst': [2],
        'path': None,
        'cmd_str': [
            'gtmis', str(img_num), 'inv_scale=1',
            'view_rect=1095,860,1105,870',"params={'algorithm': 'dispersion_extended', 'gain': 1.01, 'global_threshold': 0.1, 'min_count': 2, 'nsig_b': 6.2, 'nsig_s': 3.1, 'size': [4, 4]}"
        ],
        'token': 'dummy_4_now',
    }

    req_get = requests.get(
        uni_url, stream = True, params = full_cmd, timeout = 15
    )
    req_head = req_get.headers.get('content-length', 0)
    total_size = int(req_head) + 1
    print("total_size =" + str(total_size))
    block_size = int(total_size / 6 * 1024)
    max_size = 16384
    #max_size = 65536
    if block_size > max_size:
        block_size = max_size

    print("block_size =" + str(block_size))

    downloaded_size = 0
    compresed = bytes()
    for data in req_get.iter_content(block_size):
        compresed += data
        downloaded_size += block_size
        progress = int(100.0 * (downloaded_size / total_size))
        print("progress =", progress)

    end_data = zlib.decompress(compresed)
    print("get_request_real_time ... downloaded")
    #print("end_data =\n", end_data)

    d1d2_n_arr1d = np.frombuffer(end_data, dtype = float)
    d1 = int(d1d2_n_arr1d[0])
    d2 = int(d1d2_n_arr1d[1])
    np_array_out = d1d2_n_arr1d[2:].reshape(d1, d2)
    print("np_array_out =\n", np_array_out)
