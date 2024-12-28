"""
DUI's command simple stacked widgets

Author: Luis Fuentes-Montero (Luiso)
With strong help from DIALS and CCP4 teams

copyright (c) CCP4 - DLS
"""

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import subprocess, psutil
import os, sys, shutil, logging
import glob, json, time

from dui2.server.data_n_json import get_info_data, spit_out
from dui2.shared_modules import format_utils

def get_pair_list():
    return [
        ("d",       "display"                               ),
        ("h",       "history"                               ),
        ("ls",      "get_dir_ls"                            ),
        ("dp",      "dir_path"                              ),
        ("dl",      "display_log"                           ),
        ("rg",      "reset_graph"                           ),
        ("cl",      "closed"                                ),
        ("pr",      "run_predict_n_report"                  ),
        ("sn",      "split_node"                            ),
        ("gol",     "get_optional_command_list"             ),
        ("gr",      "get_report"                            ),
        ("gh",      "get_help"                              ),
        ("gmt",     "get_mtz"                               ),
        ("gt",      "get_template"                          ),
        ("gi",      "get_image"                             ),
        ("gis",     "get_image_slice"                       ),
        ("gmi",     "get_mask_image"                        ),
        ("gmis",    "get_mask_image_slice"                  ),
        ("grp",     "get_predictions"                       ),
        ("grl",     "get_reflection_list"                   ),
        ("gef",     "get_experiments_file"                  ),
        ("grf",     "get_reflections_file"                  ),
        ("gld",     "get_lambda"                            ),
        ("gb",      "get_bravais_sum"                       ),
        ("st",      "stop"                                  ),
        ("fdp",     "find_spots_params"                     ),
        ("idp",     "index_params"                          ),
        ("rbp",     "refine_bravais_settings_params"        ),
        ("rfp",     "refine_params"                         ),
        ("itp",     "integrate_params"                      ),
        ("smp",     "symmetry_params"                       ),
        ("csp",     "cosym_params"                          ),
        ("scp",     "scale_params"                          ),
        ("cep",     "combine_experiments_params"            ),
        ("ip",      "dials.import"                          ),
        ("gm",      "dials.generate_mask"                   ),
        ("am",      "dials.apply_mask"                      ),
        ("fd",      "dials.find_spots"                      ),

        ("fl",    "dials.filter_reflections"                ),

        ("fr",      "dials.find_rotation_axis"              ),
        ("id",      "dials.index"                           ),
        ("rb",      "dials.refine_bravais_settings"         ),
        ("ri",      "dials.reindex"                         ),
        ("rf",      "dials.refine"                          ),
        ("it",      "dials.integrate"                       ),
        ("sm",      "dials.symmetry"                        ),
        ("sc",      "dials.scale"                           ),
        ("cs",      "dials.cosym"                           ),
        ("ss",      "dials.slice_sequence"                  ),
        ("mg",      "dials.merge"                           ),
        ("ce",      "dials.combine_experiments"             ),
        ("ex",      "dials.export"                          ),
        ("sid",     "dials.ssx_index"                       ),
        ("sit",     "dials.ssx_integrate"                   ),
        ("Aaa",    "dials.align_crystal"                      ),
        ("Aaa",    "dials.anvil_correction"                   ),
        ("Aaa",    "dials.assign_experiment_identifiers"      ),
        ("Aaa",    "dials.augment_spots"                      ),
        ("Aaa",    "dials.background"                         ),
        ("Aaa",    "dials.check_indexing_symmetry"            ),
        ("Aaa",    "dials.cluster_unit_cell"                  ),
        ("Aaa",    "dials.compare_orientation_matrices"       ),
        ("Aaa",    "dials.complete_full_sphere"               ),
        ("Aaa",    "dials.compute_delta_cchalf"               ),
        ("Aaa",    "dials.convert_to_cbf"                     ),
        ("Aaa",    "dials.create_profile_model"               ),
        ("Aaa",    "dials.damage_analysis"                    ),
        ("Aaa",    "dials.data"                               ),
        ("Aaa",    "dials.detect_blanks"                      ),
        ("Aaa",    "dials.estimate_gain"                      ),
        ("Aaa",    "dials.estimate_resolution"                ),
        ("Aaa",    "dials.export_best"                        ),
        ("Aaa",    "dials.export_bitmaps"                     ),
        ("Aaa",    "dials.find_bad_pixels"                    ),
        ("Aaa",    "dials.find_hot_pixels"                    ),
        ("Aaa",    "dials.find_shared_models"                 ),
        ("Aaa",    "dials.find_spots_client"                  ),
        ("Aaa",    "dials.find_spots_server"                  ),
        ("Aaa",    "dials.frame_orientations"                 ),
        ("Aaa",    "dials.generate_distortion_maps"           ),
        ("Aaa",    "dials.geometry_viewer"                    ),
        ("Aaa",    "dials.goniometer_calibration"             ),
        ("Aaa",    "dials.image_viewer"                       ),
        ("Aaa",    "dials.import_xds"                         ),
        ("Aaa",    "dials.indexed_as_integrated"              ),
        ("Aaa",    "dials.merge_cbf"                          ),
        ("Aaa",    "dials.merge_reflection_lists"             ),
        ("Aaa",    "dials.missing_reflections"                ),
        ("Aaa",    "dials.model_background"                   ),
        ("Aaa",    "dials.modify_geometry"                    ),
        ("Aaa",    "dials.plot_Fo_vs_Fc"                      ),
        ("Aaa",    "dials.plot_reflections"                   ),
        ("Aaa",    "dials.plot_scan_varying_model"            ),
        ("Aaa",    "dials.plugins"                            ),
        ("Aaa",    "dials.powder_calibrate"                   ),
        ("Aaa",    "dials.predict"                            ),
        ("Aaa",    "dials.rbs"                                ),
        ("Aaa",    "dials.reference_profile_viewer"           ),
        ("Aaa",    "dials.refine_error_model"                 ),
        ("Aaa",    "dials.reflection_viewer"                  ),
        ("Aaa",    "dials.rl_png"                             ),
        ("Aaa",    "dials.rlv"                                ),
        ("Aaa",    "dials.rs_mapper"                          ),
        ("Aaa",    "dials.search_beam_position"               ),
        ("Aaa",    "dials.sequence_to_stills"                 ),
        ("Aaa",    "dials.shadow_plot"                        ),
        ("Aaa",    "dials.show"                               ),
        ("Aaa",    "dials.show_build_path"                    ),
        ("Aaa",    "dials.show_dist_paths"                    ),
        ("Aaa",    "dials.sort_reflections"                   ),
        ("Aaa",    "dials.split_experiments"                  ),
        ("Aaa",    "dials.spot_counts_per_image"              ),
        ("Aaa",    "dials.spot_resolution_shells"             ),
        ("Aaa",    "dials.stereographic_projection"           ),
        ("Aaa",    "dials.stills_process"                     ),
        ("Aaa",    "dials.two_theta_offset"                   ),
        ("Aaa",    "dials.two_theta_refine"                   ),
        ("Aaa",    "dials.unit_cell_histogram"                ),
        ("Aaa",    "dials.version"                            ),

    ]

def fix_alias(short_in):
    pair_list = get_pair_list()
    long_out = short_in
    for pair in pair_list:
        if pair[0] == short_in:
            long_out = pair[1]

    return long_out


def unalias_full_cmd(lst_in):
    new_full_lst = []
    for inner_lst in lst_in:
        unalias_inner_lst = []
        for elem in inner_lst:
            unalias_inner_lst.append(fix_alias(elem))

        new_full_lst.append(unalias_inner_lst)

    return new_full_lst


def find_if_in_list(inner_command):
    logging.info("find_if_in_list(multi_node)=" + str(inner_command))
    pair_list = get_pair_list()
    found_command = False
    for pair in pair_list:
        if inner_command == pair[1]:
            found_command = True

    return found_command


def add_log_line(new_line, nod_req):
    Error_Broken_Pipes = 0
    try:
        spit_out(
            str_out = new_line, req_obj = nod_req, out_type = 'utf-8'
        )

    except BrokenPipeError:
        Error_Broken_Pipes = 1

    return Error_Broken_Pipes


class CmdNode(object):
    def __init__(self, parent_lst_in = None, data_init = None):
        if data_init == None:
            data_init = ini_data()

        self.win_exe = data_init.get_win_exe()
        self.parent_node_lst = []
        try:
            for single_parent in parent_lst_in:
                self.parent_node_lst.append(single_parent.number)

        except TypeError:
            self.parent_node_lst = []

        self._lst_expt_in = []
        self._lst_refl_in = []
        self._html_rep = None
        self._predic_refl = None
        self._lst_expt_out = []
        self._lst_refl_out = []
        self.cmd_dict_ini = None
        self.lst2run = []
        self.full_cmd_lst = []
        self._run_dir = ""
        self.log_file_path = None

        self.status = "Ready"
        self.child_node_lst = []
        self.number = 0

        try:
            for single_parent in parent_lst_in:
                self.set_base_dir(single_parent._base_dir)
                for expt_2_add in single_parent._lst_expt_out:
                    self._lst_expt_in.append(expt_2_add)

                for refl_2_add in single_parent._lst_refl_out:
                    self._lst_refl_in.append(refl_2_add)

                if(
                    single_parent.lst2run[0][0] ==
                    "dials.refine_bravais_settings"
                ):
                    logging.info(
                        "after refine_bravais_settings, adding json files"
                    )
                    lst_json = glob.glob(single_parent._run_dir + os.sep + "*.json")
                    for json_2_add in lst_json:
                        self._lst_expt_in.append(json_2_add)

                if len(self._lst_expt_in) < len(self._lst_refl_in):
                    self._lst_expt_in += single_parent._lst_expt_in

                if len(self._lst_refl_in) == 0:
                    self._lst_refl_in += single_parent._lst_refl_in

        except TypeError:
            logging.info(
                "parent_lst_in =" + str(parent_lst_in) + "tmp empty "
            )

    def __call__(self, lst_in, req_obj = None):
        logging.info("\n lst_in =" + str(lst_in))
        self.full_cmd_lst.append([lst_in[0]])
        self.set_in_fil_n_par(lst_in)
        self.set_base_dir(os.getcwd())
        self.set_run_dir(self.number)
        self.nod_req = req_obj

        self.review_import_step()

        self.run_cmd(self.nod_req)

    def review_import_step(self):
        if str(self.full_cmd_lst[0][0]) == "dials.import":
            logging.info("editing (import) list cmd: " + str(self.full_cmd_lst[0]))
            new_lst_0 = []
            for part in self.full_cmd_lst[0]:
                logging.info("      editing part: " + str(part))
                if part[0:12] == "image_files=":
                    new_part = part[13:-1]

                else:
                    new_part = str(part)

                logging.info("adding(after edit): " + str(new_part))
                new_lst_0.append(new_part)

            self.full_cmd_lst[0] = new_lst_0

    def set_root(self):
        base_dir = os.getcwd()
        self.set_base_dir(base_dir)
        self._run_dir = base_dir
        self._lst_expt_in = []
        self._lst_refl_in = []
        self.full_cmd_lst = [['root']]
        self.lst2run = [['dials.root']]
        self.status = "Succeeded"

    def set_base_dir(self, dir_in = None):
        self._base_dir = dir_in

    def set_run_dir(self, num = None):
        self._run_dir = self._base_dir + os.sep + "run" + str(num)
        try:
            os.mkdir(self._run_dir)

        except FileExistsError:
            logging.info("assuming the command should run in same dir")

    def set_in_fil_n_par(self, lst_in):
        self.lst2run = []
        for inner_lst in self.full_cmd_lst:
            self.lst2run.append(list(inner_lst))

        if self.full_cmd_lst[-1][0] == "dials.reindex":
            try:
                try:
                    sol_num = int(lst_in[1])

                except(IndexError, ValueError):
                    logging.info(" ***  err catch  ***")
                    logging.info(" wrong solution number, defaulting to 1")
                    sol_num = 1

                json_file_tmp = None
                for file_str in self._lst_expt_in:
                    if "bravais_summary" in file_str:
                        json_file_tmp = str(file_str)

                if json_file_tmp is not None:
                    with open(json_file_tmp) as summary_file:
                        j_obj = json.load(summary_file)

                    change_of_basis_op = j_obj[str(sol_num)]["cb_op"]
                    input_str = "change_of_basis_op=" + str(change_of_basis_op)
                    self.full_cmd_lst[-1].append(input_str)
                    str2comp = "bravais_setting_" + str(sol_num) + ".expt"
                    for file_str in self._lst_expt_in:
                        if str2comp in file_str:
                            self._lst_expt_in = [str(file_str)]

                    self.lst2run[-1].append(" " + str(sol_num))

            except KeyError:
                logging.info("Key err catch  from attempting to reindex")

        else:
            for expt_2_add in self._lst_expt_in:
                self.full_cmd_lst[-1].append(expt_2_add)

        for refl_2_add in self._lst_refl_in:
            self.full_cmd_lst[-1].append(refl_2_add)

        if self.full_cmd_lst[-1][0] != "dials.reindex":
            for par in lst_in[1:]:
                self.full_cmd_lst[-1].append(par)
                self.lst2run[-1].append(par)

    def set_exe_files_out(self):
        self._lst_expt_out = glob.glob(self._run_dir + os.sep + "*.expt")
        #TODO reconsider if the next if is needed for failed steps
        if self._lst_expt_out == []:
            self._lst_expt_out = list(self._lst_expt_in)

        self._lst_refl_out = glob.glob(self._run_dir + os.sep + "*.refl")
        #TODO reconsider if the next if is needed for failed steps
        if self._lst_refl_out == []:
            self._lst_refl_out = list(self._lst_refl_in)

    def run_cmd(self, req_obj = None):
        self.nod_req = req_obj
        self.status = "Busy"
        inner_lst = list(self.full_cmd_lst[-1])
        is_valid_command = find_if_in_list(inner_lst[0])
        FilNotFonErr = False
        if is_valid_command:
            full_string = str(inner_lst[0])
            for nxt_pars in inner_lst[1:]:
                full_string += " " + nxt_pars

            print("\n cmd (from OS shell) = ", full_string)
            inner_lst[0] = str(shutil.which(inner_lst[0]))
            print("\n Running (from Python) >> ", inner_lst, "\n")
            try:
                self.my_proc = subprocess.Popen(
                    inner_lst,
                    shell = False,
                    cwd = self._run_dir,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.STDOUT,
                    universal_newlines = True
                )

            except FileNotFoundError:
                new_err_msg = "Dials command NOT properly installed"
                FilNotFonErr = True

        else:
            logging.info(
                " is NOT a Dials Command, NOT Running it "
            )
            self.status = "Failed"
            return

        log_line_lst = []
        self.n_Broken_Pipes = 0
        self.log_file_path = self._run_dir + os.sep + "out.log"
        new_line = None
        if self.nod_req is not None:
            try:
                self.nod_req.send_response(201)
                self.nod_req.send_header('Content-type', 'text/plain')
                self.nod_req.end_headers()

            except AttributeError:
                logging.info(
                    "Attribute Err catch, not supposed send header info #2"
                )

            try:
                str_nod_num = "node.number=" + str(self.number) + "\n"
                spit_out(
                    str_out = str_nod_num, req_obj = self.nod_req,
                    out_type = 'utf-8'
                )

            except BrokenPipeError:
                logging.info(
                    "<< BrokenPipe err catch  >> while sending nod_num"
                )

        logging.info("FilNotFonErr =" + str(FilNotFonErr))

        if FilNotFonErr:
            new_line = new_err_msg + "\n"
            self.n_Broken_Pipes += add_log_line(new_line, self.nod_req)
            log_line_lst = ["\n", new_line, "\n"]
            self.status = "Failed"
            return

        else:
            while self.my_proc.poll() is None or new_line != '':
                try:
                    new_line = self.my_proc.stdout.readline()

                except UnicodeDecodeError:
                    new_line = " <*< Unicode Decode Error >*> \n"

                self.n_Broken_Pipes += add_log_line(new_line, self.nod_req)
                log_line_lst.append(new_line[:-1])

            log_line_lst_2_write = []
            for lin_num, lin_str in enumerate(log_line_lst):
                found_non_empty = False
                for inner_lin in log_line_lst[lin_num:]:
                    if inner_lin != '':
                        found_non_empty = True

                if not found_non_empty:
                    break

                log_line_lst_2_write.append(lin_str)

        self.my_proc.stdout.close()
        if self.my_proc.poll() == 0:
            logging.info("subprocess poll 0")

        else:
            self.status = "Failed"

        if self.status != "Failed":
            self.status = "Succeeded"

        lof_file = open(self.log_file_path, "w")
        for log_line in log_line_lst_2_write:
            wrstring = log_line + "\n"
            lof_file.write(wrstring)

        lof_file.close()

        self.set_exe_files_out()

        if self.n_Broken_Pipes > 0:
            logging.info(" << BrokenPipe err catch >> while sending output")

    def generate_predict_n_report(self, req_obj = None):
        self.n_Broken_Pipes = 0
        self.nod_req = req_obj

        new_line = "HTML Report + Reflection Prediction ... START"
        self.n_Broken_Pipes += add_log_line(new_line, self.nod_req)

        tmp_html_path = self._run_dir + os.sep + "dials.report.html"

        # if dials.(scale/merge/cosym) already generated an html file
        # Dui2 should use it instead of running dials.report

        tmp_scale_html_path = self._run_dir + os.sep + "dials.scale.html"
        tmp_merge_html_path = self._run_dir + os.sep + "dials.merge.html"
        tmp_cosym_html_path = self._run_dir + os.sep + "dials.cosym.html"

        if os.path.exists(tmp_scale_html_path):
            shutil.copy(tmp_scale_html_path, tmp_html_path)
            print("Report already generated by the 'scale' cmd tool")

        elif os.path.exists(tmp_merge_html_path):
            shutil.copy(tmp_merge_html_path, tmp_html_path)
            print("Report already generated by the 'merge' cmd tool")

        elif os.path.exists(tmp_cosym_html_path):
            shutil.copy(tmp_cosym_html_path, tmp_html_path)
            print("Report already generated by the 'cosym' cmd tool")

        else:
            # running HTML report generation
            rep_lst_dat_in = ['dials.report']
            for expt_2_add in self._lst_expt_out:
                rep_lst_dat_in.append(expt_2_add)

            for refl_2_add in self._lst_refl_out:
                rep_lst_dat_in.append(refl_2_add)

            logging.info("\n running:" + str(rep_lst_dat_in))

            new_line = "Generating HTML report"
            self.n_Broken_Pipes += add_log_line(new_line, self.nod_req)

            lst_rep_out = []
            rep_lst_dat_in[0] = str(shutil.which(rep_lst_dat_in[0]))
            rep_proc = subprocess.Popen(
                rep_lst_dat_in,
                shell = False,
                cwd = self._run_dir,
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT,
                universal_newlines = True
            )
            while rep_proc.poll() is None or new_line != '':
                new_line = rep_proc.stdout.readline()
                lst_rep_out.append(new_line)

            rep_proc.stdout.close()
            # in case needed there is the output of the report here:
            #logging.info("report stdout <<< \n", lst_rep_out, "\n >>>")

        if os.path.exists(tmp_html_path):
            self._html_rep = tmp_html_path
            new_line = "HTML Report ready"

        else:
            new_line = "No need for HTML report in this step"

        self.n_Broken_Pipes += add_log_line(new_line, self.nod_req)

        # running prediction generation
        pred_lst_dat_in = ['dials.predict']
        for expt_2_add in self._lst_expt_out:
            pred_lst_dat_in.append(expt_2_add)

        logging.info("running:" + str(pred_lst_dat_in))

        new_line = "Generating Predictions"
        self.n_Broken_Pipes += add_log_line(new_line, self.nod_req)
        pred_lst_dat_in[0] = str(shutil.which(pred_lst_dat_in[0]))

        lst_pred_out = []
        pred_proc = subprocess.Popen(
            pred_lst_dat_in,
            shell = False,
            cwd = self._run_dir,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            universal_newlines = True
        )
        while pred_proc.poll() is None or new_line != '':
            new_line = pred_proc.stdout.readline()
            lst_pred_out.append(new_line)

        pred_proc.stdout.close()
        # in case needed there is the output of the prediction here:
        #logging.info("predict stdout <<< \n", lst_pred_out, "\n >>>")


        tmp_predic_path = self._run_dir + os.sep + "predicted.refl"
        if os.path.exists(tmp_predic_path):
            self._predic_refl = tmp_predic_path
            new_line = "Reflection Prediction ready"

        else:
            new_line = "No need for Reflection Prediction in this step"

        self.n_Broken_Pipes += add_log_line(new_line, self.nod_req)
        new_line = "HTML Report + Reflection Prediction ... END"
        self.n_Broken_Pipes += add_log_line(new_line, self.nod_req)

        if self.n_Broken_Pipes > 0:
            logging.info(
                "<< BrokenPipe err catch >> while sending output"
            )

    def stop_me(self):
        if self.status == "Busy":
            logging.info(
                "attempting to stop the execution of node" + str(self.number)
            )
            try:
                pid_num = self.my_proc.pid
                main_proc = psutil.Process(pid_num)
                for child in main_proc.children(recursive=True):
                    child.kill()

                main_proc.kill()

            except BrokenPipeError:
                logging.info("Broken Pipe  err catch ")

            except AttributeError:
                logging.info("No PID for << None >> process")

        else:
            logging.info(
                "node" + str(self.number) + "not running, so not stopping it"
            )

    def get_bravais_summ(self):
        brav_summ_path = str(self._run_dir + os.sep + "bravais_summary.json")
        logging.info("brav_summ_path:" + brav_summ_path)
        with open(brav_summ_path) as summary_file:
            j_obj = json.load(summary_file)

        return j_obj

class Runner(object):
    def __init__(self, recovery_data = None, dat_ini = None):
        #self.list_of_posts = []
        self.tree_output = format_utils.TreeShow()
        if dat_ini == None:
            from dui2.server.init_first import ini_data
            self.data_init = ini_data()

        else:
            self.data_init = dat_ini

        if recovery_data == None:
            self.start_from_zero()

        else:
            self._recover_state(recovery_data)

        self.num_phil_file = 0

    def start_from_zero(self):
        root_node = CmdNode(parent_lst_in = None, data_init = self.data_init)
        root_node.set_root()
        self.step_list = [root_node]
        self.bigger_lin = 0

    def run_dials_command(self, cmd_dict = None, req_obj = None):
        found_duplicated = False
        for single_step in self.step_list:
            if(
                single_step.cmd_dict_ini == cmd_dict and
                single_step.status == "Busy"
            ):
                print("\n same POST request shall not duplicate \n")
                found_duplicated = True

        if found_duplicated:
            return

        unalias_cmd_lst = unalias_full_cmd(cmd_dict["cmd_lst"])
        tmp_parent_lst_in = []
        for lin2go in cmd_dict["nod_lst"]:
            for node in self.step_list:
                if node.number == lin2go:
                    tmp_parent_lst_in.append(node)

        node2run = self._create_step(tmp_parent_lst_in)
        node2run.cmd_dict_ini = cmd_dict
        for uni_cmd in unalias_cmd_lst:
            try:
                node2run(uni_cmd, req_obj)

            except UnboundLocalError:
                logging.info("***  err catch   wrong line  not running")

        self._save_state()

    def run_dui_command(self, cmd_dict = None, req_obj = None):
        logging.info("cmd_dict(run_dui_command) = " + str(cmd_dict))
        unalias_cmd_lst = unalias_full_cmd(cmd_dict["cmd_lst"])
        logging.info("unalias_cmd_lst =" + str(unalias_cmd_lst))
        if req_obj is not None:
            try:
                if unalias_cmd_lst == [['reset_graph']]:
                    try:
                        req_obj.send_response(201)
                        req_obj.send_header('Content-type', 'text/plain')
                        req_obj.end_headers()

                    except AttributeError:
                        logging.info(
                            "Attribute Err catch," +
                            " not supposed send header info #3"
                        )

                    spit_out(
                        str_out = "err.code=0", req_obj = req_obj,
                        out_type = 'utf-8'
                    )
                    self.clear_run_dirs_n_reset()
                    spit_out(
                        str_out = "Reset tree ... Done",
                        req_obj = req_obj, out_type = 'utf-8'
                    )

                elif unalias_cmd_lst == [['run_predict_n_report']]:
                    try:
                        req_obj.send_response(201)
                        req_obj.send_header('Content-type', 'text/plain')
                        req_obj.end_headers()

                    except AttributeError:
                        logging.info(
                            "Attribute Err catch," +
                            " not supposed send header info #4"
                        )

                    spit_out(
                        str_out = "err.code=0",
                        req_obj = req_obj, out_type = 'utf-8'
                    )
                    logging.info("starting << run_predict_n_report >> ...")
                    for lin2go in cmd_dict["nod_lst"]:
                        for node in self.step_list:
                            if node.number == lin2go:
                                self.run_predict_n_report(node, req_obj)

                    spit_out(
                        str_out = "run_predict_n_report ... Done",
                        req_obj = req_obj, out_type = 'utf-8'
                    )
                    logging.info("... << run_predict_n_report >> ended")
                    print(" << run_predict_n_report >> done")
                    logging.info(" << run_predict_n_report >> done")

                elif unalias_cmd_lst == [['split_node']]:
                    try:
                        req_obj.send_response(201)
                        req_obj.send_header('Content-type', 'text/plain')
                        req_obj.end_headers()

                    except AttributeError:
                        logging.info(
                            "Attribute Err catch," +
                            " not supposed send header info #5"
                        )
                    lst_nod_out = []
                    for lin2go in cmd_dict["nod_lst"]:
                        for node in self.step_list:
                            if node.number == lin2go:
                                lst_nod_out = self.split_node(node)

                    spit_out(
                        str_out = "lst_nod_out:" + str(lst_nod_out) + "\n",
                        req_obj = req_obj, out_type = 'utf-8'
                    )

                elif unalias_cmd_lst[0][0] == 'mask_app':
                    untrusted_list = unalias_cmd_lst[0][1:]
                    phil_file_name = self.mask_app_build(untrusted_list)
                    self.run_dials_command(
                        cmd_dict = {
                            'nod_lst': cmd_dict["nod_lst"], 'cmd_lst': [
                                [
                                    'dials.generate_mask',
                                    '..'+ os.sep + phil_file_name
                                ],
                                [
                                    'dials.apply_mask',
                                    'input.mask=tmp_mask.pickle'
                                ]
                            ]
                        }, req_obj = req_obj
                    )

                elif unalias_cmd_lst == [["stop"]]:
                    for lin2go in cmd_dict["nod_lst"]:
                        try:
                            stat2add = self.step_list[lin2go].status
                            self.step_list[lin2go].stop_me()

                        except IndexError:
                            logging.info("err catch , wrong line not logging")

                        spit_out(
                            str_out = str(stat2add),
                            req_obj = req_obj, out_type = 'utf-8'
                        )

            except BrokenPipeError:
                logging.info(
                    "<< BrokenPipe err catch >> while running Dui command"
                )

        self._save_state()

    def run_get_data(self, cmd_dict):
        unalias_cmd_ini = fix_alias(cmd_dict["lst_wt_cmd"][0])
        unalias_cmd_lst = cmd_dict["lst_wt_cmd"]
        unalias_cmd_lst[0] = unalias_cmd_ini

        return_list = []
        if unalias_cmd_lst == ["display"]:
            return_list = format_utils.get_lst2show(self.step_list)
            self.tree_output(return_list)
            self.tree_output.print_output()

        elif unalias_cmd_lst == ["dir_path"]:
            return_list = [self._dir_path]

        elif unalias_cmd_lst == ["history"]:
            print("Running history command")
            lst_nod = []
            for uni in self.step_list:
                lst_nod.append(
                    {
                            "full_cmd_lst"          :uni.full_cmd_lst,
                            "_run_dir"              :uni._run_dir,
                    }
                )
            return_list = lst_nod

        elif unalias_cmd_lst == ["closed"]:
            return_list = ["closed received"]
            logging.info("received closed command")

        else:
            logging.info(
                "unalias_cmd_lst, cmd_dict = " +
                str(unalias_cmd_lst) + " , " + str(cmd_dict)
            )
            return_list = get_info_data(
                unalias_cmd_lst, cmd_dict, self.step_list
            )

        return return_list

    def clear_run_dirs_n_reset(self):
        for uni in self.step_list:
            try:
                if uni.lst2run != [['dials.root']]:
                    shutil.rmtree(str(uni._run_dir))

            except FileNotFoundError:
                logging.info(
                    "FileNotFound err catch for file" + str(uni._run_dir)
                )

        os.remove("run_data")
        self.start_from_zero()

    def run_predict_n_report(self, node, req_obj):
        str_out = " running predict and report for node:" + str(node.number)
        spit_out(
            str_out = str_out, req_obj = req_obj, out_type = 'utf-8'
        )
        node.generate_predict_n_report(req_obj)
        spit_out(
            str_out = " ... Done ", req_obj = req_obj,
            out_type = 'utf-8'
        )

    def mask_app_build(self, untrusted_list):
        logging.info("untrusted_list(mask_app) =" + str(untrusted_list))
        lst_str = []
        for single_region in untrusted_list:
            logging.info("single_region =" + str(single_region))

            if single_region[0:17] == 'multipanel.circle':
                lst_nums = single_region[18:].split(",")
                lst_str.append("untrusted {")
                lst_str.append("  panel = " + str(lst_nums[3]))
                lst_str.append(
                    "  circle =" + " " + str(lst_nums[0]) +
                    " " + str(lst_nums[1]) + " " + str(lst_nums[2])
                )
                lst_str.append("}")

            elif single_region[0:20] == 'multipanel.rectangle':
                lst_nums = single_region[21:].split(",")
                lst_str.append("untrusted {")
                lst_str.append("  panel = " + str(lst_nums[4]))
                lst_str.append(
                    "  rectangle =" + " " + str(lst_nums[0]) + " " +
                    str(lst_nums[1]) + " " + str(lst_nums[2]) + " " +
                    str(lst_nums[3])
                )
                lst_str.append("}")


        lst_str.append("output {")
        lst_str.append("  mask = tmp_mask.pickle")
        lst_str.append("}")

        self.num_phil_file += 1
        phil_file_name = 'mask_n_' + str(self.num_phil_file) + '.phil'
        logging.info("phil_file_name =" + str(phil_file_name))

        f = open(phil_file_name, 'w', encoding="utf-8")

        for str_2_write in lst_str:
            f.write(str_2_write + "\n")

        f.close()

        return phil_file_name


    def split_node(self, node):

        #TODO: don't run this if this node is not a split_experiments command

        lst_nod_out = [int(node.number)]

        with open(node.log_file_path) as myfile:
            log_line_lst = myfile.readlines()

        myfile.close()
        max_num_split = 0
        num_split = -1
        for single_line_str in log_line_lst:
            str_end = single_line_str[-6:]
            logging.info("str_end =" + str(str_end))
            if(
                str_end == '.refl\n' or
                str_end == '.expt\n'
            ):
                try:
                    str_ini = single_line_str[:-6]
                    pos4under = str_ini.rfind(" split_")
                    num_split = int(str_ini[pos4under + 7:])
                    logging.info("num_split:" + str(num_split))
                    if num_split > max_num_split:
                        max_num_split = num_split

                except ValueError:
                    logging.info(
                        "skipping the string:\n" + single_line_str + "\n"
                    )

        for junior_number in range(1, num_split + 1):
            self.find_next_number()
            new_node = CmdNode(
                parent_lst_in = None, data_init = self.data_init
            )
            new_node._base_dir       = str(node._base_dir)
            new_node.cmd_dict_ini    = node.cmd_dict_ini
            new_node.full_cmd_lst    = list(node.full_cmd_lst)
            new_node.lst2run         = list(node.lst2run)
            new_node._lst_expt_in    = list(node._lst_expt_in)
            new_node._lst_refl_in    = list(node._lst_refl_in)
            new_node.number          = int(self.bigger_lin)
            new_node.status          = str(node.status)
            new_node.parent_node_lst = list(node.parent_node_lst)

            new_node.set_run_dir(num = new_node.number)
            lst_nod_out.append(int(new_node.number))

            try:
                new_node.log_file_path = new_node._run_dir + os.sep + "out.log"
                shutil.copy(node.log_file_path, new_node._run_dir)

                lof_file_2_apend = open(new_node.log_file_path, "a")
                wrstring = "\n\n copied exp number "
                wrstring += str(junior_number) + "\n\n"
                lof_file_2_apend.write(wrstring)
                lof_file_2_apend.close()

            except FileNotFoundError:
                logging.info("No log file in:" + node.log_file_path)

            lst_cont_expt = glob.glob(
                node._run_dir + os.sep + "*" + str(junior_number) + ".expt"
            )
            logging.info("lst_cont_expt =" + str(lst_cont_expt))
            for file_n in lst_cont_expt:
                shutil.move(file_n, new_node._run_dir)

            lst_cont_refl = glob.glob(
                node._run_dir + os.sep + "*" + str(junior_number) + ".refl"
            )
            logging.info("lst_cont_refl =" + str(lst_cont_refl))
            for file_n in lst_cont_refl:
                shutil.move(file_n, new_node._run_dir)

            new_node.set_exe_files_out()

            self.step_list.append(new_node)
            for prev_step_numb in node.parent_node_lst:
                self.step_list[prev_step_numb].child_node_lst.append(
                    new_node.number
                )

        node.set_exe_files_out()
        str_out = " Done duplicating node #" + str(node.number)
        str_out += ", into " + str(num_split + 1) + " new nodes"
        logging.info("\n" + str_out + "\n")

        return lst_nod_out

    def find_next_number(self):
        tmp_big = 0
        for node in self.step_list:
            if node.number > tmp_big:
                tmp_big = node.number

        self.bigger_lin = tmp_big + 1

    def _create_step(self, prev_step_lst):
        new_step = CmdNode(
            parent_lst_in = prev_step_lst, data_init = self.data_init
        )
        self.find_next_number()
        new_step.number = self.bigger_lin
        for prev_step in prev_step_lst:
            prev_step.child_node_lst.append(new_step.number)

        self.step_list.append(new_step)
        return new_step

    def _save_state(self):
        lst_nod = []
        for uni in self.step_list:
            node = {
                        "_base_dir"             :uni._base_dir,
                        "cmd_dict_ini"          :uni.cmd_dict_ini,
                        "full_cmd_lst"          :uni.full_cmd_lst,
                        "lst2run"               :uni.lst2run,
                        "_lst_expt_in"          :uni._lst_expt_in,
                        "_lst_refl_in"          :uni._lst_refl_in,
                        "_lst_expt_out"         :uni._lst_expt_out,
                        "_lst_refl_out"         :uni._lst_refl_out,
                        "_run_dir"              :uni._run_dir,
                        "_html_rep"             :uni._html_rep,
                        "_predic_refl"          :uni._predic_refl,
                        "log_file_path"         :uni.log_file_path,
                        "number"                :uni.number,
                        "parent_node_lst"       :uni.parent_node_lst,
                        "child_node_lst"        :uni.child_node_lst,
                        "status"                :uni.status
            }
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
            new_node = CmdNode(
                parent_lst_in = None, data_init = self.data_init
            )
            new_node._base_dir       = uni_dic["_base_dir"]
            new_node.cmd_dict_ini    = uni_dic["cmd_dict_ini"]
            new_node.full_cmd_lst    = uni_dic["full_cmd_lst"]
            new_node.lst2run         = uni_dic["lst2run"]
            new_node._lst_expt_in    = uni_dic["_lst_expt_in"]
            new_node._lst_refl_in    = uni_dic["_lst_refl_in"]
            new_node._lst_expt_out   = uni_dic["_lst_expt_out"]
            new_node._lst_refl_out   = uni_dic["_lst_refl_out"]
            new_node._run_dir        = uni_dic["_run_dir"]
            new_node._html_rep       = uni_dic["_html_rep"]
            new_node._predic_refl    = uni_dic["_predic_refl"]
            new_node.log_file_path   = uni_dic["log_file_path"]
            new_node.number          = uni_dic["number"]
            new_node.child_node_lst  = uni_dic["child_node_lst"]
            new_node.parent_node_lst = uni_dic["parent_node_lst"]
            new_node.status          = uni_dic["status"]

            if new_node.status == "Busy":
                new_node.status = "Failed"

            self.step_list.append(new_node)

    def set_dir_path(self, dir_path_in):
        if dir_path_in[-1] != os.sep:
            dir_path_in += os.sep

        self._dir_path = dir_path_in

