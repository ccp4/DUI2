#from multiprocessing import Process
from dui2.client import run_client
import logging

logging.basicConfig(filename='run_dui2_client.log', level=logging.DEBUG)

def main():
    par_def = (
        ("url", 'http://127.0.0.1:45678/'),
        ("all_local", "false"),
        ("windows_exe", "false"),
    )
    run_client.main(par_def)
    print("Closing client naturally")

