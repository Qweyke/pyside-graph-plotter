from PySide6.QtWidgets import QListWidget, QWidget
from PySide6.QtCore import Qt, Signal


class LegendListWidget(QListWidget):
    func_deleted = Signal(object)

    def __init__(self, /, parent: QWidget) -> None:
        super().__init__(
            parent,
        )

    def keyPressEvent(self, event):

        # Check if the pressed key is the Delete key
        if event.key() == Qt.Key.Key_Delete:
            self.remove_selected_items()
        else:
            # Important: let other keys (arrows, etc.) work normally
            super().keyPressEvent(event)

    def remove_selected_items(self):
        for item in self.selectedItems():
            func_id = item.data(Qt.ItemDataRole.UserRole)
            row = self.row(item)
            self.takeItem(row)
            self.func_deleted.emit(func_id)
            del item
