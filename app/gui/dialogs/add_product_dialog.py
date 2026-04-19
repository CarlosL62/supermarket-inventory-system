from PySide6.QtWidgets import QDialog, QMessageBox, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from app.models.product import Product


class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        ui_file = QFile("app/gui/dialogs/add_product_dialog.ui")
        if not ui_file.open(QFile.ReadOnly):
            raise FileNotFoundError("No se pudo abrir add_product_dialog.ui")

        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        if self.ui is None:
            raise RuntimeError("No se pudo cargar la interfaz add_product_dialog.ui")

        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.resize(self.ui.size())

        self.ui.btnSave.clicked.connect(self.save_product)
        self.ui.btnCancel.clicked.connect(self.reject)

        self.product = None

    def save_product(self):
        name = self.ui.inputName.text().strip()
        barcode = self.ui.inputBarcode.text().strip()
        category = self.ui.inputCategory.text().strip()
        expiry_date = self.ui.inputExpiryDate.date().toString("yyyy-MM-dd")
        brand = self.ui.inputBrand.text().strip()
        price = self.ui.inputPrice.value()
        stock = self.ui.inputStock.value()

        if not name or not barcode or not category or not expiry_date or not brand:
            QMessageBox.warning(self, "Campos incompletos", "Todos los campos de texto son obligatorios.")
            return

        # Barcode is handled as a numeric identifier with exactly 10 digits
        if not barcode.isdigit() or len(barcode) != 10:
            QMessageBox.warning(self, "Código inválido", "El código de barras debe contener exactamente 10 dígitos.")
            return

        self.product = Product(
            name,
            barcode,
            category,
            expiry_date,
            brand,
            price,
            stock
        )

        self.accept()

    def get_product(self):
        return self.product