#uni_url = 'None'

import os, sys
from shared_modules import format_utils

class ini_data(object):
    def __init__(self):
        print("ini_data.__init__()")

    def set_data(self, par_def = None):
        init_param = format_utils.get_par(par_def, sys.argv[1:])
        global win_exe
        if init_param["windows_exe"].lower() == "true":
            win_exe = True

        else:
            win_exe = False

        print("\n win_exe =", win_exe, "\n")

    def get_win_exe(self):
        return win_exe


if __name__ == "__main__":
    init_firts = ini_data()
    print("ini_data.uni_url =", init_firts.get_url())

