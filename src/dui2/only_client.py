#from multiprocessing import Process

from dui2.client import run_client
import logging


logging.basicConfig(filename='run_dui2_client.log', level=logging.DEBUG)

def main():
    par_def = (
        ("url", 'http://127.0.0.1:45678/'),
        ("all_local", "false"),
        ("import_init", None),
        ("windows_exe", "false"),
        ("token", "dummy_4_now"),
    )
    run_client.main(par_def)
    print("Closing client naturally")

