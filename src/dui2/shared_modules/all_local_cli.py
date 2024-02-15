import sys, os, time, json, logging
from dui2.shared_modules import all_local_server, format_utils
from dui2.server.data_n_json import iter_dict
from dui2.server import multi_node
from dui2.server.init_first import ini_data


class cli_object(object):
    def __init__(self, cmd_tree_runner = None):
        self.handler = all_local_server.ReqHandler(cmd_tree_runner)
        logging.info("inside QObject")

    def run_cmd(self, str_in):

        try:
            [nod_num, str_cmd] = str_in.split(",")

        except ValueError:
            logging.info("Value Err Catch")

        cmd_in = {
            "nod_lst":[int(nod_num)], "cmd_lst":[str(str_cmd)]
        }
        self.handler.fake_post(cmd_in)
        self.handler.fake_get({"nod_lst":[0], "cmd_lst":["display"]})


def main(par_def = None):
    format_utils.print_logo()
    data_init = ini_data()
    data_init.set_data(par_def)

    init_param = format_utils.get_par(par_def, sys.argv[1:])

    run_local = True


    tree_ini_path = init_param["init_path"]
    if tree_ini_path == None:
        logging.info("\n NOT GIVEN init_path")
        logging.info(" using the dir from where the commad 'dui2_server_side' was invoqued")
        tree_ini_path = os.getcwd()

    try:
        with open("run_data") as json_file:
            runner_data = json.load(json_file)

        cmd_runner = multi_node.Runner(runner_data)

    except FileNotFoundError:
        cmd_runner = multi_node.Runner(None)

    cmd_tree_runner.set_dir_path(tree_ini_path)

    m_obj = cli_object(cmd_tree_runner = cmd_runner)

    for cmd_repeat in range(10):
        str_in = input("type: \"Node,command\":")
        m_obj.run_cmd(str_in)


if __name__ == "__main__":
    main()

