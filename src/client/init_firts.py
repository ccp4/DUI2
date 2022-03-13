#uni_url = 'None'

import os, sys

try:
    from shared_modules import format_utils

except ModuleNotFoundError:
    '''
    This trick to import the format_utils module can be
    removed once the project gets properly packaged
    '''
    comm_path = os.path.abspath(__file__)[0:-20] + "shared_modules"
    print("comm_path(init_firts): ", comm_path, "\n")
    sys.path.insert(1, comm_path)
    import format_utils


class ini_data(object):
    def __init__(self):
        print("ini_data.__init__()")

    def set_data(self):
        par_def = (
            ("url", 'http://localhost:45678/'),
        )
        print("sys.argv =", sys.argv)
        init_param = format_utils.get_par(par_def, sys.argv[1:])
        print("init_param =", init_param)
        global uni_url
        uni_url = init_param["url"]

    def get_url(self):
        return uni_url


if __name__ == "__main__":
    init_firts = ini_data()
    print("ini_data.uni_url =", init_firts.get_url())

