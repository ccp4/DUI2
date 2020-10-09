"""
DUI's command simple stacked widgets

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

from multi_node import Runner, str2dic

lst_cmd= [
"0 ls",
"0 ls",
"2 ls",
"1 ls",
"1 2 ls",
"5 ls",
"4 ls",
"0 ls",
"0 ls",
"0 ls",
"8 ls",
"9 ls",
"10 ls",
"11 ls",
"12 ls",
"13 ls",
"10 12 14 ls",
"6 ls",
]

lst_dic = [
{'nod_lst': [0], 'cmd_lst': [['ip', 'x41']]},
{'nod_lst': [0], 'cmd_lst': [['ip', 'x42']]},
{'nod_lst': [0], 'cmd_lst': [['ip', 'x43']]},
{'nod_lst': [1], 'cmd_lst': [['gm', 'untrusted.rectangle=0,1421,1258,1312', 'output.mask=tmp_mask.pickle'], ['am', 'input.mask=tmp_mask.pickle']]},
{'nod_lst': [2], 'cmd_lst': [['gm', 'untrusted.rectangle=0,1421,1258,1312', 'output.mask=tmp_mask.pickle'], ['am', 'input.mask=tmp_mask.pickle']]},
{'nod_lst': [3], 'cmd_lst': [['gm', 'untrusted.rectangle=0,1421,1258,1312', 'output.mask=tmp_mask.pickle'], ['am', 'input.mask=tmp_mask.pickle']]},
{'nod_lst': [4], 'cmd_lst': [['fd', 'nproc=9']]},
{'nod_lst': [5], 'cmd_lst': [['fd', 'nproc=9']]},
{'nod_lst': [6], 'cmd_lst': [['fd', 'nproc=9']]},
{'nod_lst': [7, 8, 9], 'cmd_lst': [['ce']]},
{'nod_lst': [10], 'cmd_lst': [['id']]},
{'nod_lst': [7], 'cmd_lst': [['id']]},
{'nod_lst': [8], 'cmd_lst': [['id']]},
{'nod_lst': [9], 'cmd_lst': [['id']]},
{'nod_lst': [12, 13, 14], 'cmd_lst': [['ce']]},
{'nod_lst': [15], 'cmd_lst': [['rf']]},
{'nod_lst': [16], 'cmd_lst': [['it', 'nproc=3']]},
{'nod_lst': [11], 'cmd_lst': [['rf']]},
{'nod_lst': [18], 'cmd_lst': [['it', 'nproc=3']]},
{'nod_lst': [11], 'cmd_lst': [['dials.refine_bravais_settings']]},
{'nod_lst': [20], 'cmd_lst': [['dials.reindex', '9']]},
{'nod_lst': [21], 'cmd_lst': [['dials.refine']]},
]

if __name__ == "__main__":

    cmd_tree_runner = Runner(None)

    cmd_dict = str2dic("display")
    cmd_tree_runner.run_dict(cmd_dict)

    for cmd_dict in lst_dic:
        cmd_tree_runner.run_dict(cmd_dict)

        cmd_dict = str2dic("display")
        cmd_tree_runner.run_dict(cmd_dict)
