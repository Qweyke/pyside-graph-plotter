from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QDialog,
    QListWidgetItem,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from gui.add_func_dialog import AddFunctionDialog
from gui.legend_list_widget import LegendListWidget
from rendering.plot_builder import PlotBuilder
from gui.res.mainwindow_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._main_ui = Ui_MainWindow()
        self._main_ui.setupUi(self)

        self.setWindowTitle("Simple Plotter")

        # Create chart widget, insert it to GUI widget's space
        self._PlotBuilder = PlotBuilder(parent=self._main_ui.plot_wdgt)
        layout = QVBoxLayout(self._main_ui.plot_wdgt)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._PlotBuilder)

        # Create legend widget, insert it to GUI widget's space
        self._funcs_legend = LegendListWidget(parent=self._main_ui.plot_wdgt)
        layout = QVBoxLayout(self._main_ui.funcs_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._funcs_legend)
        self._funcs_legend.func_deleted.connect(self._handle_del_function)

        # Connect btns
        self._main_ui.add_btn.clicked.connect(self._handle_add_function)

        # Interval values handling
        self.last_val_from = self._main_ui.from_doubleSpinBox.value()
        self._main_ui.from_doubleSpinBox.editingFinished.connect(
            self._handle_from_change
        )

        self.last_val_to = self._main_ui.to_doubleSpinBox.value()
        self._main_ui.to_doubleSpinBox.editingFinished.connect(self._handle_to_change)

    def _handle_from_change(self):
        val = self._main_ui.from_doubleSpinBox.value()
        if val >= self._main_ui.to_doubleSpinBox.value():
            self._main_ui.from_doubleSpinBox.setValue(self.last_val_from)
        else:
            self.last_val_from = val

    def _handle_to_change(self):
        val = self._main_ui.to_doubleSpinBox.value()
        if val <= self._main_ui.from_doubleSpinBox.value():
            self._main_ui.to_doubleSpinBox.setValue(self.last_val_to)
        else:
            self.last_val_to = val

    def _handle_add_function(self):
        addition_dialog = AddFunctionDialog()

        if addition_dialog.exec() == QDialog.DialogCode.Accepted:

            func_data = addition_dialog.get_data()

            fid = self._PlotBuilder.add_function(
                symbolic=func_data["expr"],
                color=func_data["color"],
                line=func_data["line"],
                left_x=self._main_ui.from_doubleSpinBox.value(),
                right_x=self._main_ui.to_doubleSpinBox.value(),
                points_qnty=self._main_ui.func_points_spinBox.value(),
                use_cones=self._main_ui.cones_checkBox.isChecked(),
            )
            func_item = QListWidgetItem(func_data["expr"])
            self._funcs_legend.addItem(func_item)

            # 4. Set the Marker Icon [cite: 21]
            pix = QPixmap(12, 12)
            pix.fill(func_data["color"])
            func_item.setIcon(QIcon(pix))
            func_item.setData(Qt.ItemDataRole.UserRole, fid)

    def _handle_del_function(self, func_id):
        self._PlotBuilder.remove_function(
            func_id,
            left_x=self._main_ui.from_doubleSpinBox.value(),
            right_x=self._main_ui.to_doubleSpinBox.value(),
            use_cones=self._main_ui.cones_checkBox.isChecked(),
            points_qnty=self._main_ui.func_points_spinBox.value(),
        )
