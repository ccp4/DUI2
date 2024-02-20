from multiprocessing import Process, Pipe
from dui2.server import image_browser_server
import logging
server_par_def = (
    ("init_path", None),
    ("port", 45678),
    ("host", "127.0.0.1"),
    #("host", "serverip"),
    ("all_local", "false"),
    ("windows_exe", "false"),
)

def main():
    pipe_server_1, pipe_server_2 = Pipe()
    prcs_serv = Process(
        target = image_browser_server.main,
        args = (server_par_def, pipe_server_2)
    )
    prcs_serv.start()
    new_port = pipe_server_1.recv()
    logging.info("# time to launch client app with port =" + str(new_port))

    par_def = (
        ("url", 'http://127.0.0.1:' + str(new_port) + '/'),
        ("all_local", "true"),
    )

    prcs_serv.join()
    logging.info("Closing server naturally")

