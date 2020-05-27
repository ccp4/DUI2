import subprocess
import os, sys
import glob, json

import out_utils

def fix_alias(short_in):
    pair_list = [
        ("d", "display" ),
        ("ip", "dials.import"),
        ("x4", "/scratch/dui_tst/X4_wide_0_to_9/*.cbf"),
        ("x41", "/scratch/dui_tst/X4_wide_10_to_19/*.cbf"),
        ("x42", "/scratch/dui_tst/X4_wide_20_to_29/*.cbf"),
        ("mg", "dials.modify_geometry"         ),
        ("gm", "dials.generate_mask"           ),
        ("am", "dials.apply_mask"              ),
        ("fd", "dials.find_spots"              ),
        ("id", "dials.index"                   ),
        ("rb", "dials.refine_bravais_settings" ),
        ("ri", "dials.reindex"                 ),
        ("rf", "dials.refine"                  ),
        ("it", "dials.integrate"               ),
        ("sm", "dials.symmetry"                ),
        ("sc", "dials.scale"                   ),
        ("ce", "dials.combine_experiments"     ),
    ]
    long_out = short_in
    for pair in pair_list:
        if pair[0] == short_in:
            print("replacing ", pair[0], " with ", pair[1])
            long_out = pair[1]

    return long_out


class CmdNode(object):
    def __init__(self, parent_lst_in = None):
        self.parent_node_lst = []
        try:
            for single_parent in parent_lst_in:
                self.parent_node_lst.append(single_parent.lin_num)

        except TypeError:
            self.parent_node_lst = []

        self._lst_expt = []
        self._lst_refl = []
        self.lst2run = []
        self._run_dir = ""

        self.status = "Ready"
        self.next_step_list = []
        self.lin_num = 0

        try:
            for single_parent in parent_lst_in:
                self.set_base_dir(single_parent._base_dir)
                for expt_2_add in glob.glob(single_parent._run_dir + "/*.expt"):
                    self._lst_expt.append(expt_2_add)

                for refl_2_add in glob.glob(single_parent._run_dir + "/*.refl"):
                    self._lst_refl.append(refl_2_add)

                lst_json = glob.glob(single_parent._run_dir + "/*.json")
                for json_2_add in lst_json:
                    self._lst_expt.append(json_2_add)

                if len(self._lst_expt) == 0:
                    self._lst_expt = single_parent._lst_expt

                if len(self._lst_refl) == 0:
                    self._lst_refl = single_parent._lst_refl

            print("self._lst_expt: ", self._lst_expt)
            print("self._lst_refl: ", self._lst_refl)

        except TypeError:
            print("parent_lst_in =", parent_lst_in, "tmp empty; ", end='')

    def __call__(self, lst_in, req_obj = None):
        print("\n lst_in =", lst_in)
        self.lst2run.append([lst_in[0]])
        self.set_in_fil_n_par(lst_in)
        self.set_base_dir(os.getcwd())
        self.set_run_dir(self.lin_num)
        self.run_cmd(req_obj)

    def set_root(self, run_dir = "/tmp/tst/", lst_expt = "/tmp/tst/imported.expt"):
        base_dir = os.getcwd()
        self.set_base_dir(base_dir)
        self._run_dir = run_dir
        self._lst_expt = []
        self._lst_refl = []
        self.lst2run = [['Root']]
        self.status = "Succeeded"

    def set_base_dir(self, dir_in = None):
            self._base_dir = dir_in

    def set_run_dir(self, num = None):
        self._run_dir = self._base_dir + "/run" + str(num)

        print("new_dir: ", self._run_dir, "\n")
        try:
            os.mkdir(self._run_dir)

        except FileExistsError:
            print("assuming the command should run in same dir")

    def set_in_fil_n_par(self, lst_in):
        if self.lst2run[-1][0] == "dials.reindex":
            try:
                try:
                    sol_num = int(lst_in[1])

                except(IndexError, ValueError):
                    print(" *** ERROR ***")
                    print(" wrong solution number, defaulting to 1")
                    sol_num = 1

                json_file_tmp = None
                for file_str in self._lst_expt:
                    if "bravais_summary" in file_str:
                        json_file_tmp = str(file_str)

                if json_file_tmp is not None:
                    with open(json_file_tmp) as summary_file:
                        j_obj = json.load(summary_file)

                    change_of_basis_op = j_obj[str(sol_num)]["cb_op"]
                    input_str = "change_of_basis_op=" + str(change_of_basis_op)
                    self.lst2run[-1].append(input_str)
                    str2comp = "bravais_setting_" + str(sol_num) + ".expt"
                    for file_str in self._lst_expt:
                        if str2comp in file_str:
                            self._lst_expt = [str(file_str)]

            except KeyError:
                print("KeyError from attempting to reindex")

        else:
            for expt_2_add in self._lst_expt:
                self.lst2run[-1].append(expt_2_add)

        for refl_2_add in self._lst_refl:
            self.lst2run[-1].append(refl_2_add)

        if self.lst2run[-1][0] != "dials.reindex":
            for par in lst_in[1:]:
                self.lst2run[-1].append(par)

    def run_cmd(self, req_obj = None):
        self.status = "Busy"
        try:
            inner_lst = self.lst2run[-1]
            print("\n Running:", inner_lst, "\n")
            proc = subprocess.Popen(
                inner_lst,
                shell = False,
                cwd = self._run_dir,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                universal_newlines = True
            )
            line = None
            n_Broken_Pipes = 0
            while proc.poll() is None or line != '':
                line = proc.stdout.readline()
                if req_obj is not None:
                    try:
                        req_obj.wfile.write(bytes(line , 'utf-8'))

                    except BrokenPipeError:
                        n_Broken_Pipes += 1

                else:
                    print(line[:-1])

            if n_Broken_Pipes > 0:
                print("\n *** BrokenPipeError *** while sending output \n")

            proc.stdout.close()
            if proc.poll() == 0:
                print("subprocess poll 0")

            else:
                print("\n  *** ERROR *** \n\n poll =", proc.poll())
                self.status = "Failed"

            if self.status != "Failed":
                self.status = "Succeeded"

        except BaseException as e:
            print("Failed to run subprocess \n ERR:", e)
            self.status = "Failed"


class Runner(object):
    def __init__(self, recovery_data):
        self.tree_output = out_utils.TreeShow()
        if recovery_data == None:
            root_node = CmdNode()
            root_node.set_root()
            self.step_list = [root_node]
            self.bigger_lin = 0

        else:
            self._recover_state(recovery_data)

    def run(self, cmd_str, req_obj = None):
        print("cmd_str =", cmd_str, "\n")

        lstpar = cmd_str.split(" ")
        lin2go_lst = []
        for single_param in lstpar:
            try:
                lin2go_lst.append(int(single_param))

            except ValueError:
                break

        if len(lin2go_lst) > 0:
            print("lin2go_lst=", lin2go_lst)

            new_par_str = ""
            for single_param in lstpar[len(lin2go_lst):]:
                new_par_str += single_param + " "

            cmd_lst = new_par_str[0:-1].split(";")
            cmd2lst = []
            for single_command in cmd_lst:
                inner_lst = single_command.split(" ")
                cmd2lst.append(inner_lst)

            print("cmd2lst: ", cmd2lst)

        else:
            print("assuming disconnected command")
            cmd2lst = [[cmd_str]]

        tmp_parent_lst_in = []
        for lin2go in lin2go_lst:
            for node in self.step_list:
                if node.lin_num == lin2go:
                    tmp_parent_lst_in.append(node)

        if len(tmp_parent_lst_in) > 0:
            node2run = self._create_step(tmp_parent_lst_in)


        unalias_lst = []
        for inner_lst in cmd2lst:
            unalias_inner_lst = []
            for elem in inner_lst:
                unalias_inner_lst.append(fix_alias(elem))

            unalias_lst.append(unalias_inner_lst)

        print("cmd2lst(unaliased) =", cmd2lst)
        return_list = []
        for uni_cmd in unalias_lst:
            print("uni_cmd", uni_cmd)

            if uni_cmd == ["display"]:
                return_list = out_utils.get_lst2show(self)
                self.tree_output(return_list)
                self.tree_output.print_output()

            else:
                try:
                    node2run(uni_cmd, req_obj)

                except UnboundLocalError:
                    print("\n *** ERROR *** \n wrong line")

            self._save_state()

        return return_list

    def _create_step(self, prev_step_lst):
        new_step = CmdNode(parent_lst_in=prev_step_lst)
        self.bigger_lin += 1
        new_step.lin_num = self.bigger_lin
        for prev_step in prev_step_lst:
            prev_step.next_step_list.append(new_step.lin_num)

        self.step_list.append(new_step)

        return new_step

    def _save_state(self):
        lst_nod = []
        for uni in self.step_list:
            node = {
                    "_base_dir"            :uni._base_dir,
                    "lst2run"              :uni.lst2run,
                    "_lst_expt"            :uni._lst_expt,
                    "_lst_refl"            :uni._lst_refl,
                    "_run_dir"             :uni._run_dir,
                    "lin_num"              :uni.lin_num,
                    "status"               :uni.status,
                    "parent_node_lst"      :uni.parent_node_lst,
                    "next_step_list"       :uni.next_step_list}

            lst_nod.append(node)

        all_dat = {
                "step_list"             :lst_nod,
                "bigger_lin"            :self.bigger_lin,
            }

        with open("run_data", "w") as fp:
            json.dump(all_dat, fp, indent=4)

    def _recover_state(self, recovery_data):
        self.step_list =    []
        self.bigger_lin =   recovery_data["bigger_lin"]

        lst_nod = recovery_data["step_list"]
        for uni_dic in lst_nod:
            new_node = CmdNode()
            new_node._base_dir       = uni_dic["_base_dir"]
            new_node.lst2run         = uni_dic["lst2run"]
            new_node._lst_expt       = uni_dic["_lst_expt"]
            new_node._lst_refl       = uni_dic["_lst_refl"]
            new_node._run_dir        = uni_dic["_run_dir"]
            new_node.lin_num         = uni_dic["lin_num"]
            new_node.status          = uni_dic["status"]
            new_node.next_step_list  = uni_dic["next_step_list"]
            new_node.parent_node_lst = uni_dic["parent_node_lst"]

            self.step_list.append(new_node)


if __name__ == "__main__":

    try:
        with open("run_data") as json_file:
            runner_data = json.load(json_file)

    except FileNotFoundError:
        runner_data = None
        print("Nothing to recover")

    cmd_tree_runner = Runner(runner_data)
    cmd_tree_runner.run("display")
    cmd_str = ""

    while cmd_str.strip() != "exit" and cmd_str.strip() != "quit":
        try:
            inp_str = "]]]>>> "
            cmd_str = str(input(inp_str))
            print("\n")

        except EOFError:
            print("Caught << EOFError >> \n  ... interrupting")
            sys.exit(0)

        except:
            print("Caught << some error >> ... interrupting")
            sys.exit(1)

        cmd_tree_runner.run(cmd_str)
        cmd_tree_runner.run("display")

