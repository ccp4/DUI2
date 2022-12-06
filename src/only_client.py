#from multiprocessing import Process
from client import run_client, logging

if __name__ == '__main__':
    par_def = (
        ("url", 'http://localhost:45678/'),
        ("all_local", "false"),
        ("windows_exe", "false"),
    )

    run_client.main(par_def)

    logging.info("Closing client naturally")

