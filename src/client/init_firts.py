#uni_url = 'None'

import os, sys
from shared_modules import format_utils

class ini_data(object):
    def __init__(self):
        print("ini_data.__init__()")

    def set_data(self, par_def = None):
        if par_def == None:
            par_def = (
                ("url", 'http://localhost:45678/'),
                ("all_local", "False"),
                ("windows_exe", "False"),
            )

        init_param = format_utils.get_par(par_def, sys.argv[1:])

        print("init_param =", init_param)
        global uni_url
        try:
            uni_url = init_param["url"]

        except KeyError:
            uni_url = None

        global run_local
        try:
            if init_param["all_local"].lower() == "true":
                run_local = True

            else:
                run_local = False

        except KeyError:
            run_local = True

        print("\n run_local =", run_local, "\n")

        global win_exe
        if init_param["windows_exe"].lower() == "true":
            win_exe = True

        else:
            win_exe = False

        print("\n win_exe =", win_exe, "\n")

    def set_tmp_dir(self, dir_path_in):
        global tmp_dir
        tmp_dir = dir_path_in

    def get_if_local(self):
        return run_local

    def get_url(self):
        return uni_url

    def get_tmp_dir(self):
        return tmp_dir

    def get_win_exe(self):
        return win_exe


if __name__ == "__main__":
    init_firts = ini_data()
    print("ini_data.uni_url =", init_firts.get_url())

