"""
DUI2's client's side output handling

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

import sys, os, requests, zlib
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

from client.exec_utils import json_data_request
from client.init_firts import ini_data

import subprocess, psutil

class LoadFiles(QThread):
    files_loaded = Signal(dict)
    loading_failed = Signal()
    progressing = Signal(int)
    def __init__(
        self, unit_URL = None, cur_nod_num = None, tmp_dir = None
    ):
        super(LoadFiles, self).__init__()
        self.uni_url = unit_URL
        self.cur_nod_num = cur_nod_num
        self.files_path_n_nod_num = {
            "tmp_exp_path"  :tmp_dir + os.sep + "req_file.expt",
            "tmp_ref_path"  :tmp_dir + os.sep + "req_file.refl",
            "cur_nod_num"   :int(cur_nod_num)
        }

    def run(self):
        print("launching << get_experiments_file >> for node: ", self.cur_nod_num)
        my_cmd = {"nod_lst" : [self.cur_nod_num],
                  "cmd_lst" : ["get_experiments_file"]}

        self.req = requests.get(
            self.uni_url, stream = True, params = my_cmd
        )
        exp_compresed = self.req.content
        try:
            full_exp_file = zlib.decompress(exp_compresed).decode('utf-8')
            tmp_file = open(self.files_path_n_nod_num["tmp_exp_path"], "w")
            tmp_file.write(full_exp_file)
            tmp_file.close()
            print("request expt, finished for node ", self.cur_nod_num)

        except zlib.error:
            print("zlib.err catch loading expt file")
            self.loading_failed.emit()
            return

        print("launching << get_reflections_file >> for node: ", self.cur_nod_num)
        my_cmd = {"nod_lst" : [self.cur_nod_num],
                  "cmd_lst" : ["get_reflections_file"]}

        self.req = requests.get(self.uni_url, stream=True, params = my_cmd)
        total_size = int(self.req.headers.get('content-length', 0)) + 1
        print("total_size =", total_size)
        block_size = int(total_size / 16)
        downloaded_size = 0
        ref_compresed = bytes()
        for data in self.req.iter_content(block_size):
            ref_compresed += data
            downloaded_size += block_size
            progress = int(100.0 * (downloaded_size / total_size))
            self.progressing.emit(progress)

        try:
            full_ref_file = zlib.decompress(ref_compresed)
            tmp_file = open(self.files_path_n_nod_num["tmp_ref_path"], "wb")
            tmp_file.write(full_ref_file)
            tmp_file.close()
            print("request refl, finished for node ", self.cur_nod_num)

        except zlib.error:
            print("zlib.err catch loading refl file")
            self.loading_failed.emit()
            return

        self.files_loaded.emit(self.files_path_n_nod_num)

    def kill_proc(self):
        print("\n kill_proc(LoadFiles) \n")
        self.req.close()


class LaunchReciprocalLattice(QThread):
    def __init__(self, exp_path, ref_path):
        super(LaunchReciprocalLattice, self).__init__()
        self.exp_path = exp_path
        self.ref_path = ref_path
        data_init = ini_data()
        self.win_exe = data_init.get_win_exe()

    def run(self):
        cmd_lst = [
            "dials.reciprocal_lattice_viewer",
            self.exp_path, self.ref_path,
        ]
        try:
            print("\n\n win_exe =", self.win_exe)
            if self.win_exe:
                cmd_lst[0] += ".exe"

            print("\n Running:", cmd_lst, "\n")
            self.my_proc = subprocess.Popen(
                cmd_lst, shell = False,
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT,
                universal_newlines = True
            )

        except FileNotFoundError:
            print(
                "unable to run:", cmd_lst,
                " <<FileNotFound err catch >> "
            )
            self.my_proc = None
            return

        new_line = None
        while self.my_proc.poll() is None or new_line != '':
            new_line = self.my_proc.stdout.readline()
            if len(new_line) > 1:
                print(new_line)

        self.my_proc.stdout.close()
        if self.my_proc.poll() == 0:
            print("subprocess poll 0")

        else:
            print("\n  ***  err catch  *** \n poll =", self.my_proc.poll())

    def kill_proc(self):
        if os.path.exists(self.exp_path):
            os.remove(self.exp_path)

        if os.path.exists(self.exp_path):
            os.remove(self.exp_path)

        try:
            pid_num = self.my_proc.pid
            main_proc = psutil.Process(pid_num)
            print("try 2 kill children procs")
            for child in main_proc.children(recursive=True):
                child.kill()

            print("try 2 kill main proc")
            main_proc.kill()

        except psutil.NoSuchProcess:
            print("Err Catch NoSuchProcess")

        except AttributeError:
            print("No PID for << None >> process")


class HandleReciprocalLatticeView(QObject):
    get_nod_num = Signal(int)
    def __init__(self, parent = None):
        super(HandleReciprocalLatticeView, self).__init__(parent)
        self.main_obj = parent
        print("HandleReciprocalLatticeView(__init__)")
        data_init = ini_data()
        self.uni_url = data_init.get_url()
        self.tmp_dir = data_init.get_tmp_dir()
        print("tmp_dir =", self.tmp_dir)
        self.running = False
        self.main_obj.window.progressBar.setRange(0, 100)
        self.main_obj.window.progressBar.setValue(0)

    def launch_RL_view(self, nod_num):
        print("Launching Reciprocal Lattice View for node: ", nod_num)
        self.quit_kill_all()
        self.load_thread = LoadFiles(
            unit_URL = self.uni_url, cur_nod_num = nod_num,
            tmp_dir = self.tmp_dir
        )
        self.load_thread.files_loaded.connect(self.new_files)
        self.load_thread.loading_failed.connect(self.failed_loading)
        self.load_thread.progressing.connect(self.p_bar_pos)

        self.load_thread.start()
        self.main_obj.window.progressBar.setValue(5)
        self.running = True

    def p_bar_pos(self, pos):
        in_pos = int(float(pos) * 0.9 + 10.0)
        self.main_obj.window.progressBar.setValue(in_pos)

    def new_files(self, paths_n_nod_num):
        self.paths_n_nod_num = paths_n_nod_num
        print("new_files(HandleReciprocalLatticeView)")
        print("nod_num from node:", self.paths_n_nod_num["cur_nod_num"])
        self.get_nod_num.emit(self.paths_n_nod_num["cur_nod_num"])

    def do_launch_RL(self):
        self.launch_RL_thread = LaunchReciprocalLattice(
            self.paths_n_nod_num["tmp_exp_path"],
            self.paths_n_nod_num["tmp_ref_path"]
        )
        self.launch_RL_thread.finished.connect(self.ended)
        self.launch_RL_thread.start()
        self.running = True
        self.main_obj.window.progressBar.setValue(100)

    def failed_loading(self):
        print("\n not running reciprocal_lattice_viewer, wrong node \n")
        self.running = False
        self.main_obj.window.progressBar.setValue(0)

    def quit_kill_all(self):
        try:
            self.load_thread.kill_proc()
            self.load_thread.quit()
            self.load_thread.wait()

        except AttributeError:
            print("Not loading files yet")

        try:
            self.launch_RL_thread.kill_proc()
            self.launch_RL_thread.quit()
            self.launch_RL_thread.wait()

        except AttributeError:
            print("No RL launched yet")

        self.running = False
        self.main_obj.window.progressBar.setValue(0)

    def change_node(self, new_node):
        print("\n changing node (HandleReciprocalLatticeView) to: ", new_node)
        print("Running =", self.running, "\n")
        if self.running:
            self.launch_RL_view(new_node)

    def ended(self):
        print("RL viewer ended")
        self.running = False
        self.main_obj.window.progressBar.setValue(0)


class HandleLoadStatusLabel(QObject):
    def __init__(self, parent = None):
        super(HandleLoadStatusLabel, self).__init__(parent)
        self.main_obj = parent

    def load_started(self):
        self.main_obj.window.OutuputStatLabel.setStyleSheet(
            "QLabel { background-color : green; color : yellow; }"
        )
        self.main_obj.window.OutuputStatLabel.setText('  Loading  ')
        self.main_obj.parent_app.processEvents()
        print("load_started (HandleLoadStatusLabel)")

    def load_progress(self, progress):
        if progress > 100:
            str_progress = "100 +"
            print("progress =", progress)

        elif progress < 0:
            str_progress = "0 -"
            print("progress =", progress)

        else:
            str_progress = str(progress)

        self.main_obj.window.OutuputStatLabel.setStyleSheet(
            "QLabel { background-color : green; color : yellow; }"
        )
        self.main_obj.window.OutuputStatLabel.setText(
            '  Loading: ' + str_progress + " %  "
        )
        self.main_obj.parent_app.processEvents()

    def load_finished(self):
        self.main_obj.window.OutuputStatLabel.setStyleSheet(
            "QLabel { background-color : white; color : blue; }"
        )
        self.main_obj.window.OutuputStatLabel.setText('  Ready  ')
        self.main_obj.parent_app.processEvents()
        print("load_finished (HandleLoadStatusLabel)")


class DoLoadHTML(QObject):
    def __init__(self, parent = None):
        super(DoLoadHTML, self).__init__(parent)
        self.main_obj = parent

        data_init = ini_data()
        self.uni_url = data_init.get_url()
        self.tmp_dir = data_init.get_tmp_dir()

        self.l_stat = HandleLoadStatusLabel(self.main_obj)

        self.main_obj.window.HtmlReport.loadStarted.connect(
            self.l_stat.load_started
        )
        self.main_obj.window.HtmlReport.loadProgress.connect(
            self.l_stat.load_progress
        )
        self.main_obj.window.HtmlReport.loadFinished.connect(
            self.l_stat.load_finished
        )
        self.lst_html = []

        first_half = """<html>
            <head>
            <title>A Sample Page</title>
            </head>
            <body>
            <h3>"""

        second_half = """</h3>
            </body>
            </html>"""

        self.not_avail_html = first_half \
        + "There is no report available for this step." \
        + second_half

        self.loading_html = first_half \
        + "  Loading ..." \
        + second_half

        self.failed_html = first_half \
        + "  Failed Connection" \
        + second_half

    def __call__(self, do_request = False):
        print("Do Request =", do_request)
        if do_request:
            print("Show HTML ... Start")
            nod_p_num = self.main_obj.curr_nod_num
            found_html = False
            for html_info in self.lst_html:
                if(
                    html_info["number"] == nod_p_num
                    and
                    len(html_info["html_report"]) > 5
                ):
                    found_html = True
                    full_file = html_info["html_report"]

            if not found_html:
                print("not found_html #1, Local Mem")
                self.main_obj.window.HtmlReport.setHtml(self.loading_html)
                self.l_stat.load_started()
                try:
                    cmd = {
                        "nod_lst":[nod_p_num],
                        "cmd_lst":["get_report"]
                    }
                    print("staring html request ...")
                    req_gt = requests.get(
                        self.uni_url, stream = True, params = cmd
                    )
                    compresed = req_gt.content
                    print("... html request ended")

                    full_file = zlib.decompress(compresed).decode('utf-8')

                    found_html = False
                    for html_info in self.lst_html:
                        if(
                            html_info["number"] == nod_p_num
                        ):
                            found_html = True
                            html_info["html_report"] = full_file

                    if not found_html:
                        print("not found_html #2, After http request")
                        self.lst_html.append(
                            {
                                "number"       :nod_p_num,
                                "html_report"   :full_file
                            }
                        )

                except ConnectionError:
                    print("\n Connection err catch (DoLoadHTML) \n")
                    full_file = ''

                except requests.exceptions.RequestException:
                    print("\n requests.exceptions.RequestException (DoLoadHTML) \n")
                    full_file = self.failed_html

                except zlib.error:
                    print("\n zlib. err catch (DoLoadHTML) \n")
                    full_file = self.not_avail_html

            if len(full_file) < 5:
                self.main_obj.window.HtmlReport.setHtml(self.not_avail_html)

            else:
                tmp_html_path = self.tmp_dir + os.sep + "temp_repo.html"
                tmp_file = open(tmp_html_path, "w")
                #
                # if Windows fails to run the next code line, type:
                #
                # set PYTHONUTF8=1
                #
                # before evoking the following:
                #
                # python .. DUI2\src\only_client.py \
                # url=http://supercomputo.cimav.edu.mx:45678 windows_exe=true
                #
                tmp_file.write(full_file)
                tmp_file.close()

                self.main_obj.window.HtmlReport.load(
                    QUrl.fromLocalFile(tmp_html_path)
                )

            print("Show HTML ... End")

        else:
            self.main_obj.window.HtmlReport.setHtml(self.not_avail_html)


class ShowLog(QObject):
    def __init__(self, parent = None):
        super(ShowLog, self).__init__(parent)
        self.main_obj = parent
        self.lst_node_log_out = []

        data_init = ini_data()
        self.uni_url = data_init.get_url()

        sys_font = QFont()
        font_point_size = sys_font.pointSize()
        my_font = QFont("Courier", font_point_size, QFont.Bold)
        my_font.setFixedPitch(True)

        self.main_obj.window.incoming_text.setFont(my_font)
        self.main_obj.window.incoming_text.setCurrentFont(my_font)

        self.set_colours(True)

    def set_colours(self, regl_font_colr):
        if regl_font_colr:
            self.red_color = QColor(255, 0, 0)
            self.green_color = QColor(0, 155, 0)
            self.blue_color = QColor(0, 0, 255)

        else:
            self.red_color = QColor(255, 155, 155)
            self.green_color = QColor(155, 255, 155)
            self.blue_color = QColor(155, 155, 255)



    def __call__(self, nod_p_num = 0, do_request = False, stat = "Busy"):
        print("Do Request =", do_request)
        if do_request:
            found_nod_num = False
            for log_node in self.lst_node_log_out:
                if log_node["number"] == nod_p_num:
                    found_nod_num = True
                    lst_log_lines = log_node["log_line_lst"]

            try:
                if not found_nod_num:
                    cmd = {"nod_lst":[nod_p_num], "cmd_lst":["display_log"]}
                    json_log = json_data_request(self.uni_url, cmd)
                    try:
                        lst_log_lines = json_log[0]
                        self.lst_node_log_out.append(
                            {
                                "number"       : nod_p_num,
                                "log_line_lst"  : lst_log_lines
                            }
                        )

                    except TypeError:
                        lst_log_lines = ["Nothing here"]

                self.main_obj.window.incoming_text.clear()
                if stat == "Busy":
                    self.main_obj.window.incoming_text.setTextColor(self.green_color)

                elif stat == "Succeeded":
                    self.main_obj.window.incoming_text.setTextColor(self.blue_color)

                else:
                    self.main_obj.window.incoming_text.setTextColor(self.red_color)

                for single_log_line in lst_log_lines:
                    self.main_obj.window.incoming_text.insertPlainText(single_log_line)
                    self.main_obj.window.incoming_text.moveCursor(QTextCursor.End)

            except IndexError:
                self.show_ready_log()

        else:
            self.show_ready_log()

    def add_line(self, new_line, nod_p_num):
        found_nod_num = False
        for log_node in self.lst_node_log_out:
            if log_node["number"] == nod_p_num:
                log_node["log_line_lst"].append(new_line)
                found_nod_num = True

        if not found_nod_num:
            self.lst_node_log_out.append(
                {
                    "number"       : nod_p_num,
                    "log_line_lst"  : [new_line]
                }
            )

        if self.main_obj.curr_nod_num == nod_p_num:
            self.main_obj.window.incoming_text.moveCursor(QTextCursor.End)
            self.main_obj.window.incoming_text.setTextColor(self.green_color)
            self.main_obj.window.incoming_text.insertPlainText(new_line)

    def show_ready_log(self):
        print('\n no need to reload "ready" log')
        self.main_obj.window.incoming_text.clear()
        self.main_obj.window.incoming_text.setTextColor(self.green_color)
        self.main_obj.window.incoming_text.insertPlainText("Ready to run: ")

