from shared_modules import all_local_gui_tst
server_par_def = (
    ("init_path", None),
    ("port", 45678),
    ("host", "localhost"),
    ("all_local", "true"),
    ("windows_exe", "false"),
)

if __name__ == '__main__':
    all_local_gui_tst.main(server_par_def)
