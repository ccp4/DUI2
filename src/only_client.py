#from multiprocessing import Process
from client import run_client
import logging

logging.basicConfig(filename='run_dui2_client.log', level=logging.DEBUG)

if __name__ == '__main__':
    par_def = (
        ("url", 'http://localhost:45678/'),
        ("all_local", "false"),
        ("windows_exe", "false"),
    )

    run_client.main(par_def)

    print("Closing client naturally")

