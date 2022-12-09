# since this is a main routine, use this to redirect stdout to a
# file -> do not swamp the console output (which is not supposed
# to be useful) - will get closed on process end.


from multiprocessing import Process, Pipe
from server import run_server
from client import run_client
import logging
logging.basicConfig(
    filename='run_dui2_all_local.log', encoding='utf-8', level=logging.DEBUG
)

server_par_def = (
    ("init_path", None),
    ("port", 45678),
    ("host", "localhost"),
    #("host", "serverip"),
    ("all_local", "true"),
    ("windows_exe", "false"),
)


if __name__ == '__main__':
    pipe_server_1, pipe_server_2 = Pipe()
    prcs_serv = Process(
        target = run_server.main,
        args = (server_par_def, pipe_server_2)
    )
    prcs_serv.start()
    new_port = pipe_server_1.recv()
    logging.info("# time to launch client app with port =" + str(new_port))

    client_par_def = (
            ("url", 'http://localhost:' + str(new_port) + '/'),
            ("all_local", "true"),
            ("windows_exe", "false"),
    )
    run_client.main(client_par_def)

    prcs_serv.join()
    logging.info("Closing server naturally")
