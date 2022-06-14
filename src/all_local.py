from multiprocessing import Process, Pipe
from server import run_server
from client import run_client

server_par_def = (
    ("init_path", None),
    ("port", 45678),
    ("host", "localhost"),
    #("host", "serverip"),
    ("all_local", "true"),
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

    pipe_client_1, pipe_client_2 = Pipe()

    par_def = (
        ("url", 'http://localhost:' + str(new_port) + '/'),
        ("all_local", "true"),
    )

    prcs_clien = Process(
        target = run_client.main,
        args = (par_def, pipe_client_2)
    )
    prcs_clien.start()

    print("# running client app =",  pipe_client_1.recv(), "\n")
    prcs_clien.join()
    print("Closing client naturally")

    prcs_serv.join()
    print("Closing server naturally")

