#from multiprocessing import Process
from client import img_view

if __name__ == '__main__':
    par_def = (
        ("url", 'http://localhost:45678/'),
        ("all_local", "false"),
    )

    img_view.main(par_def)

    print("Closing client naturally")

