from multiprocessing import Process, Pipe
from server import run_server
from client import run_client
import logging, platform

import psutil
import os

logging.basicConfig(filename='run_dui2_all_local.log', level=logging.DEBUG)

def get_other_procs():
    pid_me = int(os.getpid())
    logging.info("\n pid(me) =" + str(pid_me))
    list_2_remove = []
    for singl_proc in psutil.process_iter():
        lst4cmd = singl_proc.cmdline()

        try:
            if lst4cmd[-1][-12:] == "all_local.py":
                pid_num = int(singl_proc.pid)
                if pid_num != pid_me:
                    found_me = False
                    lst_child = []
                    main_proc = psutil.Process(pid_num)
                    for child in main_proc.children(recursive=True):
                        child_pid = child.pid
                        lst_child.append(child_pid)
                        if child_pid == pid_me:
                            found_me = True

                    if not found_me:
                        lst_child.append(pid_num)
                        for to_remove in lst_child:
                            print("removing:", to_remove)
                            proc_2_remove = psutil.Process(to_remove)
                            proc_2_remove.kill()

        except IndexError:
            pass


if __name__ == '__main__':

    print("\n platform.system()", platform.system())

    get_other_procs()

    if platform.system() == "Windows":
        win_str = "true"

    else:
        win_str = "false"

    print("win_str =", win_str, "\n")

    server_par_def = (
        ("init_path", None),
        ("port", 45678),
        ("host", "127.0.0.1"),
        #("host", "serverip"),
        ("all_local", "true"),
        ("windows_exe", win_str),
    )


    pipe_server_1, pipe_server_2 = Pipe()
    prcs_serv = Process(
        target = run_server.main,
        args = (server_par_def, pipe_server_2)
    )
    prcs_serv.start()
    new_port = pipe_server_1.recv()
    logging.info("# time to launch client app with port =" + str(new_port))
    if new_port is not None:
        client_par_def = (
                ("url", 'http://127.0.0.1:' + str(new_port) + '/'),
                ("all_local", "true"),
                ("windows_exe", win_str),
        )
        run_client.main(client_par_def)

        prcs_serv.join()
        logging.info("Closing server naturally")
