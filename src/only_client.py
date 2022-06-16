from multiprocessing import Process
from client import run_client

if __name__ == '__main__':
    par_def = (
        ("url", 'http://localhost:45678/'),
        ("all_local", "true"),
    )

    prcs_clien = Process(
        target = run_client.main,
        args = (par_def,)
    )
    prcs_clien.start()
    prcs_clien.join()
    print("Closing client naturally")

