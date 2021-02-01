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

    def __call__(self):
        print("load_html ... Start \n")
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
            self.main_obj.window.OutuputStatLabel.setText('Loading')
            self.main_obj.parent_app.processEvents()
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

        if full_file == '':
            self.main_obj.window.HtmlReport.setHtml(self.not_avail_html)

        else:
            self.main_obj.window.HtmlReport.setHtml(full_file)

        print("\n load_html ... End")

    def load_started(self):
        self.main_obj.window.OutuputStatLabel.setText('Loading')
        self.main_obj.parent_app.processEvents()
        print("load_started")

    def load_progress(self, progress):
        self.main_obj.window.OutuputStatLabel.setText(
            'Loading: ' + str(progress) + " %"
        )
        self.main_obj.parent_app.processEvents()
        print("load_progress:", progress)

    def load_finished(self):
        print("load_finished")
        self.main_obj.window.OutuputStatLabel.setText('Ready')

    def connect_loads(self):
        self.main_obj.window.HtmlReport.loadStarted.connect(self.load_started)
        self.main_obj.window.HtmlReport.loadProgress.connect(self.load_progress)
        self.main_obj.window.HtmlReport.loadFinished.connect(self.load_finished)

