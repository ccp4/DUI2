import subprocess
import os
import glob

class node(object):
    def __init__(self, old_node = None):
        self._old_node = old_node
        self._lst_expt = []
        self._lst_refl = []
        self._lst2run = [[]]
        self._run_dir = ""

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


    def set_base_dir(self, dir_in = None):
            self._base_dir = dir_in

    def set_run_dir(self, num = None):
        print("\nnum=", num, "comd", comd)
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
        self._lst2run = []
        for inner_lst in lst_in:
            self._lst2run.append([inner_lst[0]])

        self.set_imp_fil(self._lst_expt, self._lst_refl)

        for num, inner_lst in enumerate(self._lst2run):
            try:
                for par in lst_in[num][1:]:
                    inner_lst.append(par)
            except:
                print("no extra parameters")

        print("\n _lst2run:", self._lst2run, "\n")

    def run_cmd(self):

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
                line = proc.stdout.readline()[:-1]
                print("StdOut>> ", line)
                '''
                line_err = proc.stderr.readline()[:-1]
                if line_err != '':
                    print("_err>>", line_err)
                '''

            proc.stdout.close()


if __name__ == "__main__":

    cmd_lst = [
        [
            [
                "dials.modify_geometry", "geometry.detector.slow_fast_beam_centre=1279,1234"
            ]
        ],
        [
            [
                "dials.generate_mask",
                "untrusted.rectangle=0,1421,1258,1312",
                "output.mask=tmp_mask.pickle"
            ],
            [
                "dials.apply_mask",
                "input.mask=tmp_mask.pickle"
            ]
        ],
        [
            [
                "dials.find_spots",
                "nproc=5"
            ]
        ],
        [["dials.index"]],
        [["dials.refine"]],
        [
            [
                "dials.integrate",
                "nproc=3"
            ]
        ],
        [["dials.scale"]],
        ]

    old_node = node(None)
    base_dir = os.getcwd()
    old_node.set_base_dir(base_dir)

    #old_node._run_dir = "/tmp/dui2run/tst_chain/imp_dir"
    old_node._run_dir = "/tmp/tst/"

    #old_node._lst_expt = ["/tmp/dui2run/tst_chain/imp_dir/imported.expt"]
    old_node._lst_expt = ["/tmp/tst/imported.expt"]
    old_node._lst_refl = []

    for num, comd in enumerate(cmd_lst):
        new_node = node(old_node)
        new_node.set_run_dir(num)
        new_node.set_cmd_lst(comd)
        new_node.run_cmd()

        old_node = new_node



