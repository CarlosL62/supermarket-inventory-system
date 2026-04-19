from PySide6.QtWidgets import QDialog, QMessageBox, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from app.models.branch import Branch


class AddBranchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        ui_file = QFile("app/gui/dialogs/add_branch_dialog.ui")
        if not ui_file.open(QFile.ReadOnly):
            raise FileNotFoundError("No se pudo abrir add_branch_dialog.ui")

        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        if self.ui is None:
            raise RuntimeError("No se pudo cargar la interfaz add_branch_dialog.ui")

        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.setWindowTitle(self.ui.windowTitle())
        self.resize(self.ui.size())

        # Inputs
        self.input_name = self.ui.findChild(object, "inputName")
        self.input_location = self.ui.findChild(object, "inputLocation")
        self.input_entry_time = self.ui.findChild(object, "inputEntryTime")
        self.input_transfer_time = self.ui.findChild(object, "inputTransferTime")
        self.input_dispatch_interval = self.ui.findChild(object, "inputDispatchInterval")

        # Botones
        self.btn_save = self.ui.findChild(object, "btnSave")
        self.btn_cancel = self.ui.findChild(object, "btnCancel")

        self.btn_save.clicked.connect(self.save_branch)
        self.btn_cancel.clicked.connect(self.reject)

        self.branch = None

    def save_branch(self):
        name = self.input_name.text().strip()
        location = self.input_location.text().strip()
        entry_time = self.input_entry_time.value()
        transfer_time = self.input_transfer_time.value()
        dispatch_interval = self.input_dispatch_interval.value()

        # Basic validation before creating the branch
        if not name:
            QMessageBox.warning(self, "Dato inválido", "El nombre es obligatorio")
            return

        if not location:
            QMessageBox.warning(self, "Dato inválido", "La ubicación es obligatoria")
            return

        # The system assigns the branch id when saving it in the manager
        self.branch = Branch(
            0,
            name,
            location,
            entry_time,
            transfer_time,
            dispatch_interval
        )

        self.accept()

    def get_branch(self):
        return self.branch