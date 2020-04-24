import subprocess
import os
import glob

import shutil
import sys

import out_utils

class CmdNode(object):
    def __init__(self, old_node = None):
        self._old_node = old_node
        self._lst_expt = []
        self._lst_refl = []
        self._lst2run = [[None]]
        self._run_dir = ""

        self.status = "Ready"
        self.next_step_list = []
        self.cmd_lst = [["None"]]
        self.lin_num = 0

        try:
            self.set_base_dir(self._old_node._base_dir)
            print("\n old_node._base_dir =", self._old_node._base_dir)
            self._lst_expt = glob.glob(self._old_node._run_dir + "/*.expt")
            self._lst_refl = glob.glob(self._old_node._run_dir + "/*.refl")

            if len(self._lst_expt) == 0:
                self._lst_expt = self._old_node._lst_expt

            if len(self._lst_refl) == 0:
                self._lst_refl = self._old_node._lst_refl

            print("self._lst_expt: ", self._lst_expt)
            print("self._lst_refl: ", self._lst_refl)

        except:
            print("NOT _base_dir on old_node")

    def __call__(self, cmd_lst, parent):
        print("\n cmd_lst in =", cmd_lst)
        self.set_cmd_lst(list(cmd_lst))
        self.set_base_dir(os.getcwd())
        self.set_run_dir(self.lin_num)
        print("Running:", self._lst2run)
        self.run_cmd(parent)

    def set_root(self, run_dir = "/tmp/tst/", lst_expt = "/tmp/tst/imported.expt"):
        base_dir = os.getcwd()
        self.set_base_dir(base_dir)
        self._run_dir = run_dir
        self._lst_expt = lst_expt
        self._lst_refl = []
        self._lst2run = [['Root']]
        self.cmd_lst = [['Root']]
        self.status = "Succeeded"

    def set_base_dir(self, dir_in = None):
            self._base_dir = dir_in

    def set_run_dir(self, num = None):
        self._run_dir = self._base_dir + "/run" + str(num)

        print("new_dir: ", self._run_dir, "\n")
        os.mkdir(self._run_dir)

    def set_imp_fil(self, lst_expt, lst_refl):
        for inner_lst in self._lst2run:
            for expt_2_add in lst_expt:
                inner_lst.append(expt_2_add)

            for refl_2_add in lst_refl:
                inner_lst.append(refl_2_add)

    def set_cmd_lst(self, lst_in):
        self.cmd_lst = lst_in
        self._lst2run = []
        for inner_lst in self.cmd_lst:
            self._lst2run.append([inner_lst[0]])

        self.set_imp_fil(self._lst_expt, self._lst_refl)

        for num, inner_lst in enumerate(self._lst2run):
            try:
                for par in self.cmd_lst[num][1:]:
                    inner_lst.append(par)

            except:
                print("no extra parameters")

        print("\n _lst2run:", self._lst2run, "\n")

    def run_cmd(self, parent):
        self.status = "Busy"
        try:
            for inner_lst in self._lst2run:
                print("\n Running:", inner_lst, "\n")
                proc = subprocess.Popen(
                    inner_lst,
                    shell=False,
                    cwd=self._run_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
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


class Runner(object):
    def __init__(self):
        root_node = CmdNode(None)
        root_node.set_root()
        self.step_list = [root_node]
        self.bigger_lin = 0
        self.current_line = self.bigger_lin
        self.create_step(root_node)

    def run(self, cmd_lst, parent = None):
        for inner_lst in cmd_lst:
            inner_lst[0] = fix_alias(inner_lst[0])

        return_list = []

        if cmd_lst[0][0] == "goto":
            print("doing << goto >>")
            self.goto(int(cmd_lst[0][1]))

        elif cmd_lst == [["mkchi"]]:
            self.create_step(self.current_node)

        elif cmd_lst == [["mksib"]]:
            self.goto_prev()
            print("forking")
            self.create_step(self.current_node)

        elif cmd_lst == [["display"]]:

            out_utils.print_list(self)

            tree_output(self.current_line)
            return_list = tree_output.lst_out
            tree_output.print_output()

        else:
            if self.current_node.status == "Succeeded":
                self.goto_prev()
                print("forking")
                self.create_step(self.current_node)

            self.current_node(cmd_lst, parent)
            if self.current_node.status == "Failed":
                print("failed step")

        return return_list

    def create_step(self, prev_step):
        new_step = CmdNode(old_node=prev_step)

        self.bigger_lin += 1
        new_step.lin_num = self.bigger_lin
        prev_step.next_step_list.append(new_step)
        self.step_list.append(new_step)
        self.goto(self.bigger_lin)

    def goto_prev(self):
        try:
            self.goto(self.current_node._old_node.lin_num)

        except BaseException as e:
            print("can NOT fork <None> node ")

    def goto(self, new_lin):
        self.current_line = new_lin

        for node in self.step_list:
            if node.lin_num == self.current_line:
                self.current_node = node

    def get_current_node(self):
        return self.current_node


tree_output = out_utils.TreeShow()
if __name__ == "__main__":

    cmd_tree_runner = Runner()
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
        lst_cmd_lst = []
        for sub_str in lst_cmd:
            lst_cmd_lst.append(sub_str.split(" "))

        print("lst_cmd_lst:", lst_cmd_lst)
        cmd_tree_runner.run(lst_cmd_lst)
        #tree_output(cmd_tree_runner)
        #tree_output.print_output()


