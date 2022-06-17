from multiprocessing import Process, Pipe
from server import run_server

server_par_def = (
    ("init_path", None),
    ("port", 45678),
    ("host", "localhost"),
    #("host", "serverip"),
    ("all_local", "false"),
)

if __name__ == '__main__':
    pipe_server_1, pipe_server_2 = Pipe()
    prcs_serv = Process(
        target = run_server.main,
        args = (server_par_def, pipe_server_2)
    )
    prcs_serv.start()
    new_port = pipe_server_1.recv()
    print("# time to launch client app with port =",  new_port, "\n")

    par_def = (
        ("url", 'http://localhost:' + str(new_port) + '/'),
        ("all_local", "true"),
    )

    prcs_serv.join()
    print("Closing server naturally")

