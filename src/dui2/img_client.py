#from multiprocessing import Process
from dui2.client import img_view
import logging

def main():
    par_def = (
        ("url", 'http://127.0.0.1:45678/'),
        ("all_local", "false"),
        ("windows_exe", "false"),
        ("token", "dummy_4_now"),
    )

    img_view.main(par_def)

    logging.info("Closing client naturally")

