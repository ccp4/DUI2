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
            )

        init_param = format_utils.get_par(par_def, sys.argv[1:])

        print("init_param =", init_param)
        global uni_url
        uni_url = init_param["url"]
        print(
            "\n init_param['all_local'] =",
            init_param["all_local"], "\n"
        )
        global run_local
        if init_param["all_local"].lower() == "true":
            run_local = True

        else:
            run_local = False

        print("\n run_local =", run_local, "\n")

    def set_tmp_dir(self, dir_path_in):
        global tmp_dir
        tmp_dir = dir_path_in

    def get_if_local(self):
        return run_local

    def get_url(self):
        return uni_url

    def get_tmp_dir(self):
        return tmp_dir


if __name__ == "__main__":
    init_firts = ini_data()
    print("ini_data.uni_url =", init_firts.get_url())

