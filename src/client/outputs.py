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

import sys, os, requests, logging
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

from client.exec_utils import get_req_json_dat
from client.init_firts import ini_data
from client.exec_utils import get_request_shot, get_request_real_time

import subprocess, psutil, shutil, webbrowser

class LoadFiles(QThread):
    files_loaded = Signal(dict)
    loading_failed = Signal()
    progressing = Signal(int)
    def __init__(
        self, unit_URL = None, cur_nod_num = None,
        tmp_dir = None, main_handler = None
    ):
        super(LoadFiles, self).__init__()
        #self.uni_url = unit_URL
        self.cur_nod_num = cur_nod_num
        self.files_path_n_nod_num = {
            "tmp_exp_path"  :tmp_dir + os.sep + "req_file.expt",
            "tmp_ref_path"  :tmp_dir + os.sep + "req_file.refl",
            "cur_nod_num"   :int(cur_nod_num)
        }
        self.my_handler = main_handler

    def run(self):
        my_cmd = {"nod_lst" : [self.cur_nod_num],
                  "cmd_lst" : ["get_experiments_file"]}

        req_shot = get_request_shot(
            params_in = my_cmd, main_handler = self.my_handler
        )
        exp_req = req_shot.result_out()
        if exp_req == None:
            self.loading_failed.emit()
            return

        try:
            full_exp_file = exp_req.decode('utf-8')

        except AttributeError:
            self.loading_failed.emit()
            return

        tmp_file = open(self.files_path_n_nod_num["tmp_exp_path"], "w")
        tmp_file.write(full_exp_file)
        tmp_file.close()

        my_cmd = {"nod_lst" : [self.cur_nod_num],
                  "cmd_lst" : ["get_reflections_file"]}

        self.req_r_time = get_request_real_time(
            params_in = my_cmd, main_handler = self.my_handler
        )
        self.req_r_time.prog_new_stat.connect(self.emit_progr)
        self.req_r_time.load_ended.connect(self.unzip_n_emit_end)
        self.req_r_time.start()

    def emit_progr(self, percent_progr):
        self.progressing.emit(percent_progr)

    def unzip_n_emit_end(self, full_ref_file):
        self.say_good_bye()
        try:
            tmp_file = open(self.files_path_n_nod_num["tmp_ref_path"], "wb")
            tmp_file.write(full_ref_file)
            tmp_file.close()

        except TypeError:
            logging.info("Type Err catch loading refl file")
            self.loading_failed.emit()
            return

        self.files_loaded.emit(self.files_path_n_nod_num)

    def kill_proc(self):
        logging.info("\n kill_proc(LoadFiles) \n")
        self.say_good_bye()

    def say_good_bye(self):
        self.req_r_time.quit()
        self.req_r_time.wait()


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
            if self.win_exe:
                cmd_lst[0] += ".exe"

            self.my_proc = subprocess.Popen(
                cmd_lst, shell = False,
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT,
                universal_newlines = True
            )

        except FileNotFoundError:
            logging.info(
                " <<FileNotFound err catch #1>> "
            )
            self.my_proc = None
            return

        new_line = None
        while self.my_proc.poll() is None or new_line != '':
            new_line = self.my_proc.stdout.readline()
            if len(new_line) > 1:
                logging.info(str(new_line))

        self.my_proc.stdout.close()
        if self.my_proc.poll() == 0:
            logging.info("subprocess poll 0")

        else:
            logging.info("**  err catch  ** poll =" + str(self.my_proc.poll()))

    def kill_proc(self):
        if os.path.exists(self.exp_path):
            os.remove(self.exp_path)

        if os.path.exists(self.exp_path):
            os.remove(self.exp_path)

        try:
            pid_num = self.my_proc.pid
            main_proc = psutil.Process(pid_num)
            logging.info("try 2 kill children procs")
            for child in main_proc.children(recursive=True):
                child.kill()

            logging.info("try 2 kill main proc")
            main_proc.kill()

        except psutil.NoSuchProcess:
            logging.info("Err Catch NoSuchProcess")

        except AttributeError:
            logging.info("No PID for << None >> process")


class HandleReciprocalLatticeView(QObject):
    get_nod_num = Signal(int)
    def __init__(self, parent = None):
        super(HandleReciprocalLatticeView, self).__init__(parent)
        self.main_obj = parent
        self.my_handler = parent.runner_handler
        logging.info("HandleReciprocalLatticeView(__init__)")
        data_init = ini_data()
        self.uni_url = data_init.get_url()
        self.tmp_dir = data_init.get_tmp_dir()
        logging.info("tmp_dir =" + self.tmp_dir)
        self.quit_kill_all()
        self.main_obj.window.progressBar.setRange(0, 100)
        self.main_obj.window.progressBar.setValue(0)

    def launch_RL_view(self, nod_num):
        new_load_thread = LoadFiles(
            unit_URL = self.uni_url, cur_nod_num = nod_num,
            tmp_dir = self.tmp_dir, main_handler = self.my_handler
        )
        new_load_thread.files_loaded.connect(self.new_files)
        new_load_thread.loading_failed.connect(self.failed_loading)
        new_load_thread.progressing.connect(self.p_bar_pos)
        new_load_thread.start()
        self.load_thread_lst.append(new_load_thread)
        self.main_obj.window.progressBar.setValue(5)

    def p_bar_pos(self, pos):
        in_pos = int(float(pos) * 0.9 + 10.0)
        self.main_obj.window.progressBar.setValue(in_pos)

    def new_files(self, paths_n_nod_num):
        self.paths_n_nod_num = paths_n_nod_num
        logging.info("new_files(HandleReciprocalLatticeView)")
        self.get_nod_num.emit(self.paths_n_nod_num["cur_nod_num"])

    def do_launch_RL(self):
        new_launch_RL_thread = LaunchReciprocalLattice(
            self.paths_n_nod_num["tmp_exp_path"],
            self.paths_n_nod_num["tmp_ref_path"]
        )
        new_launch_RL_thread.finished.connect(self.ended)
        new_launch_RL_thread.start()
        self.launch_RL_thread_lst.append(new_launch_RL_thread)
        self.main_obj.window.progressBar.setValue(100)

    def failed_loading(self):
        logging.info("\n not running reciprocal_lattice_viewer, wrong node \n")
        self.main_obj.window.progressBar.setValue(0)

    def quit_kill_all(self):
        try:
            for load_thread in self.load_thread_lst:
                try:
                    load_thread.kill_proc()
                    load_thread.quit()
                    load_thread.wait()

                except AttributeError:
                    logging.info("Not loading files yet")

        except AttributeError:
            logging.info("Not loading files yet")

        self.load_thread_lst = []

        try:
            for launch_RL_thread in self.launch_RL_thread_lst:
                try:
                    launch_RL_thread.kill_proc()
                    launch_RL_thread.quit()
                    launch_RL_thread.wait()

                except AttributeError:
                    logging.info("No RL launched yet")

        except AttributeError:
            logging.info("No RL launched yet")

        self.launch_RL_thread_lst = []
        self.main_obj.window.progressBar.setValue(0)

    def change_node(self, new_node):
        logging.info(
            "changing node (HandleReciprocalLatticeView) to: " + str(new_node)
        )
        self.launch_RL_view(new_node)

    def ended(self):
        logging.info("RL viewer ended")
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
        logging.info("load_started (HandleLoadStatusLabel)")

    def load_progress(self, progress):
        if progress > 100:
            str_progress = "100 +"

        elif progress < 0:
            str_progress = "0 -"

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
        logging.info("load_finished (HandleLoadStatusLabel)")


class DoLoadHTML(QObject):
    def __init__(self, parent = None):
        super(DoLoadHTML, self).__init__(parent)
        self.main_obj = parent
        self.my_handler = parent.runner_handler
        data_init = ini_data()
        self.uni_url = data_init.get_url()
        self.tmp_dir = data_init.get_tmp_dir()

        self.l_stat = HandleLoadStatusLabel(self.main_obj)
        try:
            self.main_obj.window.HtmlReport.loadStarted.connect(
                self.l_stat.load_started
            )
            self.main_obj.window.HtmlReport.loadProgress.connect(
                self.l_stat.load_progress
            )
            self.main_obj.window.HtmlReport.loadFinished.connect(
                self.l_stat.load_finished
            )

        except AttributeError:
            logging.info("not working HtmlView # 1")

        self.main_obj.window.DownloadReportButton.clicked.connect(
            self.download_clicked
        )
        self.main_obj.window.OpenBrowserButton.clicked.connect(
            self.open_browser_clicked
        )

        first_half = """<html>
            <head>
            <title>A Sample Page</title>
            </head>
            <body>
            <h3>"""

        second_half = """</h3>
            </body>
            </html>"""

        self.reset_lst_html()
        self.not_avail_html = first_half \
        + "There is no report available for this step." \
        + second_half

        self.loading_html = first_half \
        + "  Loading ..." \
        + second_half

        self.failed_html = first_half \
        + "  Failed Connection" \
        + second_half

    def reset_lst_html(self):
        self.lst_html = []

    def download_clicked(self):
        logging.info("download_clicked(DoLoadHTML)")
        ini_file = os.getcwd() + os.sep + "report.html"
        fileResul = QFileDialog.getSaveFileName(
            self.main_obj.window.HtmlReport, "Download HTML File",
            ini_file, "Html Report (*.html)"
        )
        entered_file_name = fileResul[0]
        try:
            shutil.copy(self.new_file_path, entered_file_name)  ###

        except AttributeError:
            logging.info("Attribute Err catch, no path for HTML file (Download)")

        logging.info(entered_file_name + " writen to disk")

    def open_browser_clicked(self):
        logging.info("open_browser_clicked(DoLoadHTML)")
        try:
            webbrowser.open(self.new_file_path)

        except AttributeError:
            logging.info(
                "Attribute Err catch, no path for HTML file (OpenBrowser)"
            )

    def __call__(self, do_request = False):
        logging.info("Do Request =" + str(do_request))
        if do_request:
            logging.info("Show HTML ... Start")
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
                logging.info("not found_html #1, Local Mem")
                try:
                    self.main_obj.window.HtmlReport.setHtml(self.loading_html)

                except AttributeError:
                    logging.info("not working HtmlView # 2")

                self.l_stat.load_started()
                try:
                    cmd = {
                        "nod_lst":[nod_p_num],
                        "cmd_lst":["get_report"]
                    }
                    logging.info("staring html request ...")

                    req_shot = get_request_shot(
                        params_in = cmd, main_handler = self.my_handler
                    )

                    req_file = req_shot.result_out()
                    if req_file == None:
                        full_file = self.not_avail_html

                    else:
                        full_file = req_file.decode('utf-8')

                    logging.info("... html request ended")

                    found_html = False
                    for html_info in self.lst_html:
                        if(
                            html_info["number"] == nod_p_num
                        ):
                            found_html = True
                            html_info["html_report"] = full_file

                    if not found_html:
                        logging.info("not found_html #2, After http request")
                        self.lst_html.append(
                            {
                                "number"       :nod_p_num,
                                "html_report"   :full_file
                            }
                        )

                except AttributeError:
                    logging.info("\n Connection err catch (DoLoadHTML) \n")
                    full_file = ''

                except ConnectionError:
                    logging.info("\n Connection err catch (DoLoadHTML) \n")
                    full_file = ''

                except requests.exceptions.RequestException:
                    logging.info(
                        "\nrequests.exceptions.RequestException (DoLoadHTML)\n"
                    )
                    full_file = self.failed_html

            if len(full_file) < 5:
                try:
                    self.main_obj.window.HtmlReport.setHtml(
                        self.not_avail_html
                    )

                except AttributeError:
                    logging.info("not working HtmlView # 3")

            else:
                curr_htmp_file_name = "report_node_" + str(nod_p_num) + ".html"
                tmp_html_path = self.tmp_dir + os.sep + curr_htmp_file_name
                self.new_file_path = str(tmp_html_path)
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
                try:
                    self.main_obj.window.HtmlReport.load(
                        QUrl.fromLocalFile(tmp_html_path)
                    )

                except AttributeError:
                    logging.info("not working HtmlView # 4")

            logging.info("Show HTML ... End")
            self.l_stat.load_finished()

        else:
            try:
                self.main_obj.window.HtmlReport.setHtml(self.not_avail_html)

            except AttributeError:
                logging.info("not working HtmlView # 5")


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

    def set_colours(self, regular_colours):
        if regular_colours:
            self.red_color = QColor(255, 0, 0)
            self.green_color = QColor(0, 155, 0)
            self.blue_color = QColor(0, 0, 255)

        else:
            self.red_color = QColor(255, 155, 155)
            self.green_color = QColor(155, 255, 155)
            self.blue_color = QColor(155, 155, 255)

    def __call__(self, nod_p_num = 0, do_request = False, stat = "Busy"):
        logging.info("Do Request =" + str(do_request))
        if do_request:
            found_nod_num = False
            for log_node in self.lst_node_log_out:
                if log_node["number"] == nod_p_num:
                    found_nod_num = True
                    lst_log_lines = log_node["log_line_lst"]

            try:
                if not found_nod_num:
                    cmd = {"nod_lst":[nod_p_num], "cmd_lst":["display_log"]}
                    lst_req = get_req_json_dat(
                        params_in = cmd,
                        main_handler = self.main_obj.runner_handler
                    )
                    json_log = lst_req.result_out()
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
                    self.main_obj.window.incoming_text.setTextColor(
                        self.green_color
                    )

                elif stat == "Succeeded":
                    self.main_obj.window.incoming_text.setTextColor(
                        self.blue_color
                    )

                else:
                    self.main_obj.window.incoming_text.setTextColor(
                        self.red_color
                    )

                for single_log_line in lst_log_lines:
                    self.main_obj.window.incoming_text.insertPlainText(
                        single_log_line
                    )
                    self.main_obj.window.incoming_text.moveCursor(
                        QTextCursor.End
                    )

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
        logging.info('\n no need to reload "ready" log')
        self.main_obj.window.incoming_text.clear()
        self.main_obj.window.incoming_text.setTextColor(self.green_color)
        self.main_obj.window.incoming_text.insertPlainText("Ready to run: ")

