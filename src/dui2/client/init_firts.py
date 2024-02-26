#uni_url = 'None'

import os, sys, logging
from dui2.shared_modules import format_utils

class ini_data(object):
    def __init__(self):
        logging.info("ini_data.__init__()")

    def set_data(self, par_def = None):
        if par_def == None:
            par_def = (
                ("url", 'http://127.0.0.1:45678/'),
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

        print("URL(client side) = ", uni_url)

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

    def get_tmp_dir(self):
        return tmp_dir

    def get_win_exe(self):
        return win_exe


if __name__ == "__main__":
    init_firts = ini_data()
    logging.info("ini_data.uni_url =" + str(init_firts.get_url()))

