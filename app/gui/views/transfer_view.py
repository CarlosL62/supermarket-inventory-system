from PySide6.QtWidgets import QMessageBox


class TransferView:
    def __init__(self, branch_manager, source_combo, destination_combo, product_combo, quantity_input, result_label, parent=None):
        self.branch_manager = branch_manager
        self.source_combo = source_combo
        self.destination_combo = destination_combo
        self.product_combo = product_combo
        self.quantity_input = quantity_input
        self.result_label = result_label
        self.parent = parent

    def get_branch_label(self, branch):
        return f"{branch.id} - {branch.name}"

    def load_branch_options(self):
        branches = self.branch_manager.get_branches()

        self.source_combo.clear()
        self.destination_combo.clear()

        for branch in branches:
            label = self.get_branch_label(branch)
            self.source_combo.addItem(label, branch.id)
            self.destination_combo.addItem(label, branch.id)

        self.load_product_options()

    def load_product_options(self):
        self.product_combo.clear()

        source_id = self.source_combo.currentData()
        if source_id is None:
            return

        source_branch = self.branch_manager.find_by_id(source_id)
        if source_branch is None:
            return

        for product in source_branch.inventory.get_all_products():
            label = f"{product.name} - {product.barcode} - Stock: {product.stock}"
            self.product_combo.addItem(label, product.barcode)

    def execute_transfer(self):
        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()
        barcode = self.product_combo.currentData()
        quantity = self.quantity_input.value()

        if source_id is None or destination_id is None:
            QMessageBox.warning(self.parent, "Datos incompletos", "Seleccione sucursal origen y destino")
            return

        if barcode is None:
            QMessageBox.warning(self.parent, "Sin producto", "Seleccione un producto para transferir")
            return

        success, message, path, total_weight = self.branch_manager.transfer_product(
            source_id,
            destination_id,
            barcode,
            quantity
        )

        if not success:
            self.result_label.setText(f"Resultado: {message}")
            QMessageBox.warning(self.parent, "Transferencia no realizada", message)
            return

        path_text = " -> ".join(str(branch_id) for branch_id in path)
        result_text = f"Resultado: {message} | Ruta: {path_text} | Peso total: {total_weight}"
        self.result_label.setText(result_text)
        self.load_product_options()
        QMessageBox.information(self.parent, "Transferencia realizada", result_text)