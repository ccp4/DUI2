from multiprocessing import Process, Pipe
from server import run_server

par_def = (
    ("init_path", None),
    ("port", 45678),
    ("host", "localhost"),
    #("host", "serverip"),
    ("all_local", "true"),
)

if __name__ == '__main__':
    pipe_connect_1, pipe_connect_2 = Pipe()
    p = Process(target = run_server.main, args = (par_def, pipe_connect_2))
    p.start()
    print("# port =",  pipe_connect_1.recv(), "\n")
    p.join()
    print("Closing naturally")
