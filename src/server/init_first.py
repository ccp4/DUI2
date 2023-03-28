#uni_url = 'None'

import os, sys, logging
from shared_modules import format_utils

class ini_data(object):
    def __init__(self):
        logging.info("ini_data.__init__()")

    def set_data(self, par_def = None):
        init_param = format_utils.get_par(par_def, sys.argv[1:])
        logging.info("init_param =" + str(init_param))
        global win_exe
        if init_param["windows_exe"].lower() == "true":
            win_exe = True

        else:
            win_exe = False

        logging.info("win_exe = " + str(win_exe))

    def get_win_exe(self):
        return False
        #return win_exe


if __name__ == "__main__":
    init_firts = ini_data()
    logging.info("ini_data.uni_url =" + str(init_firts.get_url()))

