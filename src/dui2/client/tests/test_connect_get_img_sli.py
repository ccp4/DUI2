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

uni_url = 'http://127.0.0.1:45678/'
#uni_url = 'http://127.0.0.1:45679/'
#uni_url = 'http://supercomputo.cimav.edu.mx:45678/'


if __name__ == "__main__":
    '''full_cmd = {
        'nod_lst': [4], 'path': None,
        'cmd_str': ['gmis', '0', 'inv_scale=2', 'view_rect=408,248,2043,2205']
    }'''

    full_cmd = {
        'nod_lst': [4], 'path': None,
        'cmd_str':['gmis', '0', 'inv_scale=1', 'view_rect=0,0,624,747']
    }

    try:
        req_get = requests.get(
            uni_url, stream = True, params = full_cmd, timeout = 65
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
            #self.prog_new_stat.emit(progress)
            print("progress =", progress)

        end_data = zlib.decompress(compresed)
        print("get_request_real_time ... downloaded")

        tmp_off = '''
    except zlib.error:
        print("zlib. err catch(get_request_real_time) <<")
        end_data = None
        '''

    except ConnectionError:
        print("\n Connection err catch (get_request_real_time) \n")
        end_data = None

    except requests.exceptions.RequestException:
        print(
            "\n requests.exceptions.ReqExp (get_request_real_time) \n"
        )
        end_data = None

    #self.load_ended.emit(end_data)
    print("load_ended")

