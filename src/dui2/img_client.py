#from multiprocessing import Process
from client import img_view
import logging

if __name__ == '__main__':
    par_def = (
        ("url", 'http://127.0.0.1:45678/'),
        ("all_local", "false"),
        ("windows_exe", "false"),
    )

    img_view.main(par_def)

    logging.info("Closing client naturally")

