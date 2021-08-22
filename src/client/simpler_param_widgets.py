"""
DUI2's simpler parameters widgets

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

import logging
import sys

default_max_nproc = 4

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from PySide2.QtGui import *

def _get_all_direct_layout_widget_children(parent):
    """Walk a widget tree and get all non-QLayout direct children

    Args:
        parent(QLayout): The layout to walk

    Returns:
        (List[QWidget]): Any widgets directly attached to layouts in this
    """
    children = []
    if isinstance(parent, QLayout):
        for child in [parent.itemAt(i) for i in range(parent.count())]:
            children.extend(_get_all_direct_layout_widget_children(child))

    elif hasattr(parent, "widget"):
        if parent.widget():
            children.append(parent.widget())

    return children


class DefaultComboBox(QComboBox):
    """A ComboBox initialised with a list of items and keeps track of which one
    is default"""

    def __init__(self, local_path, items, default_index=0):
        super(DefaultComboBox, self).__init__()
        self.local_path = local_path
        self.item_list = items
        self.default_index = default_index
        for item in items:
            self.addItem(item)

        self.setCurrentIndex(self.default_index)


class SimpleParamTab(QWidget):
    """Base class shared by all simple parameter tabs"""

    item_changed = Signal(str, str)
    item_to_remove = Signal(str)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

                else:
                    self.clearLayout(item.layout())


    def update_param(self, param_in, value_in):
        print("\n update_param (Simple)", param_in, value_in)

        for widget in self.children():
            widget_path = None
            if isinstance(widget, QLineEdit):
                widget_path = widget.local_path
                widget_value = str(widget.text())

            if isinstance(widget, QDoubleSpinBox) or isinstance(widget, QSpinBox):
                widget_path = widget.local_path
                widget_value = str(widget.value())

            if isinstance(widget, DefaultComboBox):
                widget_path = widget.local_path
                widget_value = str(widget.currentText())

            if widget_path == param_in:
                if widget_value == value_in:
                    print("No need to change parameter (same value)")

                else:
                    self.do_emit = False
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value_in))

                    if(
                        isinstance(widget, QDoubleSpinBox) or
                        isinstance(widget, QSpinBox)
                    ):
                        try:
                            widget.setValue(float(value_in))

                        except ValueError:
                            print("\n param_in =", param_in)
                            print("value_in =", value_in, "\n")
                            print("skipping attempt to convert string to float \n")


                    if isinstance(widget, DefaultComboBox):
                        widget.setCurrentText(str(value_in))

                    self.do_emit = True

    def update_all_pars(self, tup_lst_pars):
        print("\n (Simple Widget) \n time to update par to:", tup_lst_pars, "\n")
        for par_dic in tup_lst_pars[0]:
            self.update_param(par_dic["name"], par_dic["value"])

    def do_emit_signal(self, str_path, str_value):
        if self.do_emit:
            self.item_changed.emit(str_path, str_value)

        self.do_emit = True #TODO: find out if this line is needed

    def spnbox_finished(self):
        print("spnbox_finished")
        sender = self.sender()
        value = sender.value()
        str_path = str(sender.local_path)
        #TODO find out why there is a "item_to_remove" signal
        if sender.specialValueText() and value == sender.minimum():
            self.item_to_remove.emit(str_path)

        else:
            str_value = str(value)
            self.do_emit_signal(str_path, str_value)

    def combobox_changed(self, value):
        print("combobox_changed")
        sender = self.sender()
        str_value = str(sender.item_list[value])
        str_path = str(sender.local_path)

        #TODO find out why there is a "item_to_remove" signal
        if sender.currentIndex() == sender.default_index:
            self.item_to_remove.emit(str_path)
        else:
            self.do_emit_signal(str_path, str_value)

    def line_changed(self):
        sender = self.sender()
        str_value = sender.text()
        str_path = str(sender.local_path)

        self.do_emit_signal(str_path, str_value)


class ImportTmpWidg(QWidget):
    item_changed = Signal(str, str)
    def __init__(self, parent = None):
        super(ImportTmpWidg, self).__init__(parent)
        self.do_emit = True
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        new_label = QLabel("Import:")
        new_label.setFont(QFont(
            "Monospace", font_point_size + 3, QFont.Bold
        ))
        self.imp_txt = QLineEdit()
        self.imp_txt.editingFinished.connect(self.line_changed)

        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(new_label)
        self.main_vbox.addWidget(self.imp_txt)
        self.main_vbox.addWidget(QLabel(" "))
        self.setLayout(self.main_vbox)


    def reset_pars(self):
        self.imp_txt.setText("")

    def line_changed(self):
        sender = self.sender()
        str_value = sender.text()
        str_path = " "
        self.item_changed.emit(str_path, str_value)

    def update_all_pars(self, tup_lst_pars):
        print(
            "update_all_pars(ImportTmpWidg)",
            tup_lst_pars, "... dummy"
        )

    def update_param(self, str_path, str_value):
        print(
            "update_param(ImportTmpWidg)",
            str_path, str_value, "... dummy"
        )

class MaskTmpWidg(SimpleParamTab):
    def __init__(self, parent = None):
        super(MaskTmpWidg, self).__init__(parent)
        self.do_emit = True
        sys_font = QFont()
        font_point_size = sys_font.pointSize()

        new_label = QLabel(" ...  (TMP)   Apply Mask:    ")
        new_label.setFont(QFont(
            "Monospace", font_point_size + 3, QFont.Bold
        ))

        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(QLabel(" "))
        self.main_vbox.addWidget(new_label)
        self.main_vbox.addWidget(QLabel(" "))
        self.setLayout(self.main_vbox)

    def reset_pars(self):
        print("\n reset_pars(MaskTmpWidg) \n")


class FindspotsSimplerParameterTab(SimpleParamTab):
    """
    This widget is the tool for tunning the simpler and most common parameters
    in the spot-finder, this widget is the first to appear once the button
    "Find Sots" at the left side of the GUI is clicked
    """

    def __init__(self, parent=None):
        super(FindspotsSimplerParameterTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):
        xds_gain_label = QLabel("Gain")
        xds_gain_spn_bx = QDoubleSpinBox()
        xds_gain_spn_bx.local_path = "spotfinder.threshold.dispersion.gain"
        xds_gain_spn_bx.setValue(1.0)
        xds_gain_spn_bx.editingFinished.connect(self.spnbox_finished)

        xds_sigma_background_label = QLabel("Sigma background")
        xds_sigma_background_spn_bx = QDoubleSpinBox()
        xds_sigma_background_spn_bx.setValue(6.0)
        xds_sigma_background_spn_bx.local_path = (
            "spotfinder.threshold.dispersion.sigma_background"
        )
        xds_sigma_background_spn_bx.editingFinished.connect(self.spnbox_finished)

        xds_sigma_strong_label = QLabel("Sigma strong")
        xds_sigma_strong_spn_bx = QDoubleSpinBox()
        xds_sigma_strong_spn_bx.setValue(3.0)
        xds_sigma_strong_spn_bx.local_path = (
            "spotfinder.threshold.dispersion.sigma_strong"
        )
        xds_sigma_strong_spn_bx.editingFinished.connect(self.spnbox_finished)

        xds_global_threshold_label = QLabel("Global threshold")
        xds_global_threshold_spn_bx = QDoubleSpinBox()
        xds_global_threshold_spn_bx.setMaximum(9999.99)
        xds_global_threshold_spn_bx.local_path = (
            "spotfinder.threshold.dispersion.global_threshold"
        )
        xds_global_threshold_spn_bx.editingFinished.connect(self.spnbox_finished)


        xds_gain_hb = QHBoxLayout()
        xds_gain_hb.addWidget(xds_gain_label)
        xds_gain_hb.addWidget(xds_gain_spn_bx)
        self.main_v_layout.addLayout(xds_gain_hb)

        xds_sigma_background_hb = QHBoxLayout()
        xds_sigma_background_hb.addWidget(xds_sigma_background_label)
        xds_sigma_background_hb.addWidget(xds_sigma_background_spn_bx)
        self.main_v_layout.addLayout(xds_sigma_background_hb)

        xds_sigma_strong_hb = QHBoxLayout()
        xds_sigma_strong_hb.addWidget(xds_sigma_strong_label)
        xds_sigma_strong_hb.addWidget(xds_sigma_strong_spn_bx)
        self.main_v_layout.addLayout(xds_sigma_strong_hb)

        xds_global_threshold_hb = QHBoxLayout()
        xds_global_threshold_hb.addWidget(xds_global_threshold_label)
        xds_global_threshold_hb.addWidget(xds_global_threshold_spn_bx)
        self.main_v_layout.addLayout(xds_global_threshold_hb)

        hbox_lay_nproc = QHBoxLayout()
        label_nproc = QLabel("Number of Processes")
        # label_nproc.setPalette(palette_object)
        # label_nproc.setFont( QFont("Monospace", 10))
        hbox_lay_nproc.addWidget(label_nproc)

        self.box_nproc = QSpinBox()
        self.box_nproc.local_path = "spotfinder.mp.nproc"

        self.box_nproc.editingFinished.connect(self.spnbox_finished)
        hbox_lay_nproc.addWidget(self.box_nproc)
        self.main_v_layout.addLayout(hbox_lay_nproc)

        self.main_v_layout.addStretch()


        self.lst_var_widg = _get_all_direct_layout_widget_children(self.main_v_layout)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()

    def set_max_nproc(self):
        cpu_max_proc = default_max_nproc
        self.box_nproc.setValue(cpu_max_proc)
        return cpu_max_proc


class IndexSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tunning the simpler and most common parameters
    in the indexer, this widget is the first to appear once the button
    "Index" at the left side of the GUI is clicked
    """

    def __init__(self, phl_obj=None, parent=None):
        super(IndexSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):

        hbox_method = QHBoxLayout()
        label_method_62 = QLabel("Indexing method")
        hbox_method.addWidget(label_method_62)
        box_method_62 = DefaultComboBox("indexing.method", ["fft3d", "fft1d",
            "real_space_grid_search", "low_res_spot_match"])
        box_method_62.currentIndexChanged.connect(self.combobox_changed)

        hbox_method.addWidget(box_method_62)

        max_cell_label = QLabel("Max cell")
        max_cell_spn_bx = QDoubleSpinBox()
        max_cell_spn_bx.setSingleStep(5.0)
        max_cell_spn_bx.local_path = "indexing.max_cell"
        max_cell_spn_bx.setSpecialValueText("Auto")
        max_cell_spn_bx.editingFinished.connect(self.spnbox_finished)

        space_group_label = QLabel("Space group")
        space_group_line = QLineEdit()
        # Simple validator to allow only characters in H-M symbols
        regex = QRegExp("[ABCPIFR][0-9a-d\-/:nmHR]+")
        validatorHM = QRegExpValidator(regex)
        space_group_line.setValidator(validatorHM)
        space_group_line.local_path = "indexing.known_symmetry.space_group"
        space_group_line.editingFinished.connect(self.line_changed)

        unit_cell_label = QLabel("Unit cell")
        unit_cell_line = QLineEdit()
        regex = QRegExp("[0-9\., ]+")
        validatorUC = QRegExpValidator(regex)
        unit_cell_line.setValidator(validatorUC)
        unit_cell_line.local_path = "indexing.known_symmetry.unit_cell"
        unit_cell_line.editingFinished.connect(self.line_changed)


        self.main_v_layout.addLayout(hbox_method)

        qf = QFormLayout()
        qf.addRow(max_cell_label, max_cell_spn_bx)
        qf.addRow(space_group_label, space_group_line)
        qf.addRow(unit_cell_label, unit_cell_line)
        self.main_v_layout.addLayout(qf)

        self.main_v_layout.addStretch()

        self.lst_var_widg = _get_all_direct_layout_widget_children(self.main_v_layout)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class RefineBravaiSimplerParamTab(SimpleParamTab):
    def __init__(self, parent=None):
        super(RefineBravaiSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):
        hbox_lay_outlier_algorithm = QHBoxLayout()
        label_outlier_algorithm = QLabel("Outlier rejection algorithm")

        hbox_lay_outlier_algorithm.addWidget(label_outlier_algorithm)
        box_outlier_algorithm = DefaultComboBox(
            "refinement.reflections.outlier.algorithm", ["null", "Auto", "mcd",
            "tukey", "sauter_poon"], default_index=1)
        box_outlier_algorithm.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_outlier_algorithm.addWidget(box_outlier_algorithm)
        self.main_v_layout.addLayout(hbox_lay_outlier_algorithm)

        self.main_v_layout.addStretch()


        self.lst_var_widg = []
        self.lst_var_widg.append(box_outlier_algorithm)
        self.lst_var_widg.append(label_outlier_algorithm)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class RefineSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tunning the simpler and most common parameters
    in the refiner, this widget is the first to appear once the button
    "Refine" at the left side of the GUI is clicked
    """

    def __init__(self, parent=None):
        super(RefineSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):

        hbox_lay_scan_varying = QHBoxLayout()

        label_scan_varying = QLabel("Scan varying refinement")

        hbox_lay_scan_varying.addWidget(label_scan_varying)

        box_scan_varying = DefaultComboBox("refinement.parameterisation.scan_varying",
            ["True", "False", "Auto"], default_index=2)
        box_scan_varying.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_scan_varying.addWidget(box_scan_varying)
        self.main_v_layout.addLayout(hbox_lay_scan_varying)

        ###########################################################################

        hbox_lay_outlier_algorithm = QHBoxLayout()
        label_outlier_algorithm = QLabel("Outlier rejection algorithm")

        hbox_lay_outlier_algorithm.addWidget(label_outlier_algorithm)
        box_outlier_algorithm = DefaultComboBox(
            "refinement.reflections.outlier.algorithm", ["null", "Auto", "mcd",
            "tukey", "sauter_poon"], default_index=1)
        box_outlier_algorithm.currentIndexChanged.connect(self.combobox_changed)

        hbox_lay_outlier_algorithm.addWidget(box_outlier_algorithm)
        self.main_v_layout.addLayout(hbox_lay_outlier_algorithm)

        self.main_v_layout.addStretch()


        self.lst_var_widg = []
        self.lst_var_widg.append(box_scan_varying)
        self.lst_var_widg.append(label_scan_varying)

        self.lst_var_widg.append(box_outlier_algorithm)
        self.lst_var_widg.append(label_outlier_algorithm)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class IntegrateSimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tunning the simpler and most common parameters
    in the integrate algorithm, this widget is the first to appear once the button
    "Integrate" at the left side of the GUI is clicked
    """

    def __init__(self, parent=None):
        super(IntegrateSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):

        PrFit_lay_out = QHBoxLayout()
        label_PrFit = QLabel("Use profile fitting")
        PrFit_lay_out.addWidget(label_PrFit)

        PrFit_comb_bx = DefaultComboBox("integration.profile.fitting",
            ["True", "False", "Auto"])
        PrFit_comb_bx.currentIndexChanged.connect(self.combobox_changed)

        PrFit_lay_out.addWidget(PrFit_comb_bx)
        self.main_v_layout.addLayout(PrFit_lay_out)

        hbox_lay_algorithm_53 = QHBoxLayout()
        label_algorithm_53 = QLabel("Background algorithm")
        hbox_lay_algorithm_53.addWidget(label_algorithm_53)

        box_algorithm_53 = DefaultComboBox("integration.background.algorithm",
            ["simple", "null", "median", "gmodel", "glm"], default_index=4)
        box_algorithm_53.currentIndexChanged.connect(self.combobox_changed)

        hbox_lay_algorithm_53.addWidget(box_algorithm_53)
        self.main_v_layout.addLayout(hbox_lay_algorithm_53)

        hbox_d_min = QHBoxLayout()
        label_d_min = QLabel("High resolution limit")
        hbox_d_min.addWidget(label_d_min)
        d_min_spn_bx = QDoubleSpinBox()
        d_min_spn_bx.local_path = "prediction.d_min"
        d_min_spn_bx.setSpecialValueText("None")
        d_min_spn_bx.setValue(0.0)
        hbox_d_min.addWidget(d_min_spn_bx)
        d_min_spn_bx.editingFinished.connect(self.spnbox_finished)
        self.main_v_layout.addLayout(hbox_d_min)

        hbox_lay_nproc = QHBoxLayout()
        label_nproc = QLabel("Number of Processes")
        # label_nproc.setFont( QFont("Monospace", 10))
        hbox_lay_nproc.addWidget(label_nproc)

        self.box_nproc = QSpinBox()

        self.box_nproc.local_path = "integration.mp.nproc"
        self.box_nproc.editingFinished.connect(self.spnbox_finished)
        hbox_lay_nproc.addWidget(self.box_nproc)
        self.main_v_layout.addLayout(hbox_lay_nproc)

        self.main_v_layout.addStretch()
        #self.box_nproc.item_list = None
        self.lst_var_widg = _get_all_direct_layout_widget_children(self.main_v_layout)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()

    def set_max_nproc(self):
        cpu_max_proc = default_max_nproc
        self.box_nproc.setValue(cpu_max_proc)
        return cpu_max_proc


class SymmetrySimplerParamTab(SimpleParamTab):
    """
    This widget is the tool for tunning the simpler and most common parameters
    in the symmetry command, this widget is the first to appear once the button
    "Symmetry" at the left side of the GUI is clicked
    """

    def __init__(self, parent=None):
        super(SymmetrySimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):
        label_d_min = QLabel("High resolution limit")
        hbox_d_min = QHBoxLayout()
        hbox_d_min.addWidget(label_d_min)

        d_min_spn_bx = QDoubleSpinBox()
        d_min_spn_bx.local_path = "d_min"
        d_min_spn_bx.setSpecialValueText("Auto")
        d_min_spn_bx.setValue(0.0)
        hbox_d_min.addWidget(d_min_spn_bx)

        d_min_spn_bx.editingFinished.connect(self.spnbox_finished)

        self.main_v_layout.addLayout(hbox_d_min)

        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(d_min_spn_bx)
        self.lst_var_widg.append(label_d_min)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class ScaleSimplerParamTab(SimpleParamTab):

    """
    This widget is the tool for tunning the simpler and most common parameters
    in the scale command, this widget is the first to appear once the button
    "Scale" at the left side of the GUI is clicked
    """

    def __init__(self, parent=None):
        super(ScaleSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):

        #TODO: review the parameters here, the need updating

        hbox_lay_mod = QHBoxLayout()
        label_mod = QLabel("Model")

        hbox_lay_mod.addWidget(label_mod)
        box_mod = DefaultComboBox("model", ["physical", "array", "KB"])
        box_mod.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_mod.addWidget(box_mod)

        hbox_lay_wgh_opt_err = QHBoxLayout()
        label_wgh_opt_err = QLabel("Error optimisation model")

        hbox_lay_wgh_opt_err.addWidget(label_wgh_opt_err)
        box_wgh_opt_err = DefaultComboBox("weighting.error_model.error_model",
            ["basic", "None"])
        box_wgh_opt_err.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_wgh_opt_err.addWidget(box_wgh_opt_err)
        """
        weighting {
          error_model {
            error_model = *basic None
        """

        hbox_d_min = QHBoxLayout()
        d_min_label = QLabel("High resolution limit")
        d_min_spn_bx = QDoubleSpinBox()
        d_min_spn_bx.local_path = "cut_data.d_min"
        d_min_spn_bx.setSpecialValueText("None")
        d_min_spn_bx.setValue(0.0)
        hbox_d_min.addWidget(d_min_label)
        hbox_d_min.addWidget(d_min_spn_bx)

        d_min_spn_bx.editingFinished.connect(self.spnbox_finished)

        self.main_v_layout.addLayout(hbox_lay_mod)
        self.main_v_layout.addLayout(hbox_lay_wgh_opt_err)
        self.main_v_layout.addLayout(hbox_d_min)


        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(box_mod)
        self.lst_var_widg.append(label_mod)
        self.lst_var_widg.append(box_wgh_opt_err)
        self.lst_var_widg.append(label_wgh_opt_err)
        self.lst_var_widg.append(d_min_spn_bx)
        self.lst_var_widg.append(d_min_label)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class CombineExperimentSimplerParamTab(SimpleParamTab):
    def __init__(self, parent=None):
        super(CombineExperimentSimplerParamTab, self).__init__()
        self.do_emit = True
        self.main_v_layout = QVBoxLayout()
        self.build_pars()
        self.setLayout(self.main_v_layout)

    def build_pars(self):
        hbox_lay_dummy_1 = QHBoxLayout()
        label_dummy_1 = QLabel("Dummy TMP selector")

        hbox_lay_dummy_1.addWidget(label_dummy_1)
        box_dummy_2 = DefaultComboBox(
            "scope_1.scope_2.definition", [
                "opt 1", "opt 2", "None", "Auto"
            ], default_index=1)
        box_dummy_2.currentIndexChanged.connect(self.combobox_changed)
        hbox_lay_dummy_1.addWidget(box_dummy_2)
        self.main_v_layout.addLayout(hbox_lay_dummy_1)

        self.main_v_layout.addStretch()

        self.lst_var_widg = []
        self.lst_var_widg.append(box_dummy_2)
        self.lst_var_widg.append(label_dummy_1)

    def reset_pars(self):
        self.clearLayout(self.main_v_layout)
        self.build_pars()


class TmpTstWidget(QWidget):
    def __init__(self, parent=None):
        super(TmpTstWidget, self).__init__()
        self.do_emit = True

        #my_widget = MaskTmpWidg(self)
        my_widget = ImportTmpWidg(self)
        #my_widget = FindspotsSimplerParameterTab(self)
        #my_widget = IndexSimplerParamTab(self)
        #my_widget = RefineBravaiSimplerParamTab(self)
        #my_widget = RefineSimplerParamTab(self)
        #my_widget = IntegrateSimplerParamTab(self)
        #my_widget = SymmetrySimplerParamTab(self)
        #my_widget = ScaleSimplerParamTab(self)
        #my_widget = CombineExperimentSimplerParamTab(self)


        my_box = QVBoxLayout()
        my_box.addWidget(my_widget)
        self.setLayout(my_box)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = TmpTstWidget()
    ex.show()
    sys.exit(app.exec_())
