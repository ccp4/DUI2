from multiprocessing import Process, Pipe
from dui2.server import run_server
import logging

logging.basicConfig(filename='run_dui2_server.log', level=logging.DEBUG)

server_par_def = (
    ("init_path", None),
    ("port", 45678),
    ("host", "127.0.0.1"),
    #("host", "serverip"),
    ("all_local", "false"),
    ("windows_exe", "false"),
)

if __name__ == '__main__':
    pipe_server_1, pipe_server_2 = Pipe()
    prcs_serv = Process(
        target = run_server.main,
        args = (server_par_def, pipe_server_2)
    )
    prcs_serv.start()
    try:
        new_port = pipe_server_1.recv()
        print("# time to launch client app with port =" +  str(new_port))
        prcs_serv.join()
        print("Closing server naturally")

    except KeyboardInterrupt:
        print("Interrupted with Keyboard, parent event")


