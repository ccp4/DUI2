import subprocess
import os, sys
import glob, json

import out_utils


def fix_alias(short_in):
    pair_list = [
        ("d", "display" ),
        ("g", "goto"    ),
        ("c", "mkchi"   ),
        ("s", "mksib"   ),
        ("mg", "dials.modify_geometry"  ),
        ("gm", "dials.generate_mask"    ),
        ("am", "dials.apply_mask"       ),
        ("fd", "dials.find_spots"       ),
        ("id", "dials.index"            ),
        ("rf", "dials.refine"           ),
        ("it", "dials.integrate"        ),
        ("sm", "dials.symmetry"         ),
        ("sc", "dials.scale"            ),
    ]
    long_out = short_in
    for pair in pair_list:
        if pair[0] == short_in:
            print("replacing ", pair[0], " with ", pair[1])
            long_out = pair[1]

    return long_out



class CmdNode(object):
    def __init__(self, old_node = None):
        try:
            self._old_node = old_node.lin_num

        except AttributeError:
            self._old_node = None

        self._lst_expt = []
        self._lst_refl = []
        self.lst2run = []
        self._run_dir = ""

        self.status = "Ready"
        self.next_step_list = []
        self.lin_num = 0

        try:
            self.set_base_dir(old_node._base_dir)
            self._lst_expt = glob.glob(old_node._run_dir + "/*.expt")
            self._lst_refl = glob.glob(old_node._run_dir + "/*.refl")

            if len(self._lst_expt) == 0:
                self._lst_expt = old_node._lst_expt

            if len(self._lst_refl) == 0:
                self._lst_refl = old_node._lst_refl

            print("self._lst_expt: ", self._lst_expt)
            print("self._lst_refl: ", self._lst_refl)

        except AttributeError:
            print("creating node without parent")

    def __call__(self, lst_in, parent):
        print("\n lst_in =", lst_in)

        self.lst2run.append([lst_in[0]])
        self.set_imp_fil(self._lst_expt, self._lst_refl)
        for par in lst_in[1:]:
            self.lst2run[-1].append(par)

        self.set_base_dir(os.getcwd())
        self.set_run_dir(self.lin_num)
        print("Running:", self.lst2run)
        self.run_cmd(parent)

    def set_root(self, run_dir = "/tmp/tst/", lst_expt = "/tmp/tst/imported.expt"):
        base_dir = os.getcwd()
        self.set_base_dir(base_dir)
        self._run_dir = run_dir
        self._lst_expt = lst_expt
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

    def set_imp_fil(self, lst_expt, lst_refl):
        for expt_2_add in lst_expt:
            self.lst2run[-1].append(expt_2_add)

        for refl_2_add in lst_refl:
            self.lst2run[-1].append(refl_2_add)

    def run_cmd(self, parent):
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
            while proc.poll() is None or line != '':
                line = proc.stdout.readline()
                try:
                    parent.wfile.write(bytes(line , 'utf-8'))

                except AttributeError:
                    print(line[:-1])

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
        if recovery_data == None:
            root_node = CmdNode(None)
            root_node.set_root()
            self.step_list = [root_node]
            self.bigger_lin = 0
            self.current_line = self.bigger_lin
            self.create_step(root_node)

        else:
            self.recover_state(recovery_data)

    def run(self, cmd2lst, parent = None):
        for inner_lst in cmd2lst:
            inner_lst[0] = fix_alias(inner_lst[0])

        print("cmd2lst(unaliased) =", cmd2lst)
        return_list = []
        for uni_cmd in cmd2lst:
            print("uni_cmd", uni_cmd)

            if uni_cmd[0] == "goto":
                print("doing << goto >>")
                self.goto(int(uni_cmd[1]))

            elif uni_cmd == ["mkchi"]:
                self.create_step(self.current_node)

            elif uni_cmd == ["mksib"]:
                self.goto_prev()
                print("forking")
                self.create_step(self.current_node)

            elif uni_cmd == ["display"]:
                return_list = out_utils.print_list(self)
                tree_output(self.current_line, return_list)
                tree_output.print_output()

            else:
                self.current_node(uni_cmd, parent)
                if self.current_node.status == "Failed":
                    print("failed step")

            self.save_state()

        return return_list

    def create_step(self, prev_step):
        new_step = CmdNode(old_node=prev_step)
        self.bigger_lin += 1
        new_step.lin_num = self.bigger_lin
        prev_step.next_step_list.append(new_step.lin_num)
        self.step_list.append(new_step)
        self.goto(self.bigger_lin)

    def goto_prev(self):
        try:
            self.goto(self.current_node._old_node)

        except BaseException as e:
            print("can NOT fork <None> node ")

    def goto(self, new_lin):
        self.current_line = new_lin
        for node in self.step_list:
            if node.lin_num == self.current_line:
                self.current_node = node

    def get_current_node(self):
        return self.current_node

    def save_state(self):
        lst_nod = []
        for uni in self.step_list:
            node = {
                    "_base_dir"            :uni._base_dir,
                    "lst2run"             :uni.lst2run,
                    "_lst_expt"            :uni._lst_expt,
                    "_lst_refl"            :uni._lst_refl,
                    "_run_dir"             :uni._run_dir,
                    "lin_num"              :uni.lin_num,
                    "status"               :uni.status,
                    "_old_node"            :uni._old_node,
                    "next_step_list"       :uni.next_step_list}

            lst_nod.append(node)

        all_dat = {
                "step_list"             :lst_nod,
                "bigger_lin"            :self.bigger_lin,
                "current_line"          :self.current_line,
            }

        with open("run_data", "w") as fp:
            json.dump(all_dat, fp, indent=4)

    def recover_state(self, recovery_data):
        self.step_list =    []
        self.bigger_lin =   recovery_data["bigger_lin"]
        self.current_line = recovery_data["current_line"]

        lst_nod = recovery_data["step_list"]
        for uni_dic in lst_nod:
            new_node = CmdNode(None)
            new_node._base_dir       = uni_dic["_base_dir"]
            new_node.lst2run        = uni_dic["lst2run"]
            new_node._lst_expt       = uni_dic["_lst_expt"]
            new_node._lst_refl       = uni_dic["_lst_refl"]
            new_node._run_dir        = uni_dic["_run_dir"]
            new_node.lin_num         = uni_dic["lin_num"]
            new_node.status          = uni_dic["status"]
            new_node.next_step_list  = uni_dic["next_step_list"]
            new_node._old_node       = uni_dic["_old_node"]

            if new_node.lin_num == self.current_line:
                self.current_node = new_node

            self.step_list.append(new_node)



tree_output = out_utils.TreeShow()
if __name__ == "__main__":

    try:
        with open("run_data") as json_file:
            runner_data = json.load(json_file)

    except FileNotFoundError:
        runner_data = None
        print("Nothing to recover")

    cmd_tree_runner = Runner(runner_data)
    cmd_tree_runner.run([["display"]])
    command = ""

    while command.strip() != "exit" and command.strip() != "quit":
        try:
            inp_str = "lin [" + str(cmd_tree_runner.current_line) + "] >>> "
            command = str(input(inp_str))
            print("\n")

        except EOFError:
            print("Caught << EOFError >> \n  ... interrupting")
            sys.exit(0)

        except:
            print("Caught << some error >> ... interrupting")
            sys.exit(1)

        print("command =", command, "\n")

        lst_cmd = command.split(";")
        lst_cmd2lst = []
        for sub_str in lst_cmd:
            lst_cmd2lst.append(sub_str.split(" "))

        print("lst_cmd2lst:", lst_cmd2lst)
        cmd_tree_runner.run(lst_cmd2lst)
        cmd_tree_runner.run([["display"]])

