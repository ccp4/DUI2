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

import sys, os, requests
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

from exec_utils import json_data_request, uni_url

class DoLoadHTML(QObject):
    def __init__(self, parent = None):
        super(DoLoadHTML, self).__init__(parent)
        self.main_obj = parent
        self.connect_loads()
        self.lst_html = []

        self.not_avail_html = """<html>
            <head>
            <title>A Sample Page</title>
            </head>
            <body>
            <h3>There is no report available for this step.</h3>
            </body>
            </html>"""
        self.loading_html = """<html>
            <head>
            <title>A Sample Page</title>
            </head>
            <body>
            <h3>  Loading ...</h3>
            </body>
            </html>"""

        self.failed_html = """<html>
            <head>
            <title>A Sample Page</title>
            </head>
            <body>
            <h3>  Failed Connection</h3>
            </body>
            </html>"""

    def __call__(self):
        print("network load_html ... Start")
        nod_p_num = self.main_obj.gui_state["current_nod_num"]
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
            self.main_obj.window.HtmlReport.setHtml(self.loading_html)
            self.main_obj.window.OutuputStatLabel.setStyleSheet(
                "QLabel { background-color : green; color : yellow; }"
            )
            self.main_obj.window.OutuputStatLabel.setText('  Loading  ')
            self.main_obj.parent_app.processEvents()
            try:
                cmd = {
                    "nod_lst":[nod_p_num],
                    "cmd_lst":["get_report"]
                }
                r_g = requests.get(
                    'http://localhost:8080/', stream = True, params = cmd
                )
                full_file = ''
                while True:
                    tmp_dat = r_g.raw.readline()
                    #line_str = str(tmp_dat.decode('utf-8'))
                    line_str = tmp_dat.decode('utf-8')
                    if line_str[-7:] == '/*EOF*/':
                        print('/*EOF*/ received')
                        break

                    else:
                        full_file += line_str

                found_html = False
                for html_info in self.lst_html:
                    if(
                        html_info["number"] == nod_p_num
                    ):
                        found_html = True
                        html_info["html_report"] = full_file

                if not found_html:
                    self.lst_html.append(
                        {
                            "number"       :nod_p_num,
                            "html_report"   :full_file
                        }
                    )
            except ConnectionError:
                print("\n ConnectionError (DoLoadHTML) \n")
                full_file = ''

            except requests.exceptions.RequestException:
                print("\n requests.exceptions.RequestException (DoLoadHTML) \n")
                full_file = self.failed_html

        if len(full_file) < 5:
            self.main_obj.window.HtmlReport.setHtml(self.not_avail_html)

        else:
            self.main_obj.window.HtmlReport.setHtml(full_file)

        print("network load_html ... End")

    def load_started(self):
        self.main_obj.window.OutuputStatLabel.setStyleSheet(
            "QLabel { background-color : green; color : yellow; }"
        )
        self.main_obj.window.OutuputStatLabel.setText('  Loading  ')
        self.main_obj.parent_app.processEvents()
        print("RAM load_started")

    def load_progress(self, progress):
        self.main_obj.window.OutuputStatLabel.setStyleSheet(
            "QLabel { background-color : green; color : yellow; }"
        )
        self.main_obj.window.OutuputStatLabel.setText(
            '  Loading: ' + str(progress) + " %  "
        )
        self.main_obj.parent_app.processEvents()

    def load_finished(self):
        print("RAM load_finished")
        self.main_obj.window.OutuputStatLabel.setStyleSheet(
            "QLabel { background-color : white; color : blue; }"
        )
        self.main_obj.window.OutuputStatLabel.setText('  Ready  ')

    def connect_loads(self):
        self.main_obj.window.HtmlReport.loadStarted.connect(self.load_started)
        self.main_obj.window.HtmlReport.loadProgress.connect(self.load_progress)
        self.main_obj.window.HtmlReport.loadFinished.connect(self.load_finished)

    def set_output_as_ready(self):
        self.main_obj.window.incoming_text.clear()
        self.main_obj.window.incoming_text.insertPlainText("Ready to run: ")
        self.main_obj.window.HtmlReport.setHtml(self.not_avail_html)


class ShowLog(QObject):
    def __init__(self, parent = None):
        super(ShowLog, self).__init__(parent)
        self.main_obj = parent
        self.lst_node_log_out = []


    def __call__(self, nod_p_num = 0):
        found_nod_num = False
        for log_node in self.lst_node_log_out:
            if log_node["number"] == nod_p_num:
                found_nod_num = True
                lst_log_lines = log_node["log_line_lst"]

        try:
            if not found_nod_num:
                cmd = {"nod_lst":[nod_p_num], "cmd_lst":["display_log"]}
                json_log = json_data_request(uni_url, cmd)
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
            for single_log_line in lst_log_lines:
                self.main_obj.window.incoming_text.insertPlainText(single_log_line)
                self.main_obj.window.incoming_text.moveCursor(QTextCursor.End)

        except IndexError:
            print('\n no need to reload "ready" log')

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

        if self.main_obj.gui_state["current_nod_num"] == nod_p_num:
            self.main_obj.window.incoming_text.moveCursor(QTextCursor.End)
            self.main_obj.window.incoming_text.insertPlainText(new_line)
