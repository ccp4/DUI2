from shared_modules import all_local_server
server_par_def = (
    ("init_path", None),
    ("port", 45678),
    ("host", "localhost"),
    ("all_local", "true"),
    ("windows_exe", "false"),
)

if __name__ == '__main__':
    all_local_server.main(server_par_def)
