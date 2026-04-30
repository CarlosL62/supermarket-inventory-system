from PySide6.QtWidgets import QMessageBox


class TransferView:
    def __init__(self, branch_manager, source_combo, destination_combo, product_combo, quantity_input, criterion_combo, result_label, parent=None):
        self.branch_manager = branch_manager
        self.source_combo = source_combo
        self.destination_combo = destination_combo
        self.product_combo = product_combo
        self.quantity_input = quantity_input
        self.criterion_combo = criterion_combo
        self.result_label = result_label
        self.parent = parent

        self.source_combo.currentIndexChanged.connect(self.preview_transfer)
        self.destination_combo.currentIndexChanged.connect(self.preview_transfer)
        self.product_combo.currentIndexChanged.connect(self.preview_transfer)
        self.quantity_input.valueChanged.connect(self.preview_transfer)
        self.criterion_combo.currentIndexChanged.connect(self.preview_transfer)

    def get_branch_label(self, branch):
        return f"{branch.id} - {branch.name}"

    def get_branch_name(self, branch_id):
        branch = self.branch_manager.find_by_id(branch_id)
        return branch.name if branch is not None else str(branch_id)

    def get_path_names_text(self, path):
        return " -> ".join(self.get_branch_name(branch_id) for branch_id in path)

    def get_connection_totals(self, path):
        total_time = 0
        total_cost = 0

        if not path:
            return total_time, total_cost

        for index in range(len(path) - 1):
            source_id = path[index]
            destination_id = path[index + 1]

            for neighbor_id, time_weight, cost_weight in self.branch_manager.graph.get_neighbors(source_id):
                if neighbor_id == destination_id:
                    total_time += time_weight
                    total_cost += cost_weight
                    break

        return total_time, total_cost

    def estimate_internal_processing_time(self, path):
        total_time = 0

        for index, branch_id in enumerate(path):
            branch = self.branch_manager.find_by_id(branch_id)

            if branch is None:
                continue

            if index == 0:
                total_time += branch.dispatch_interval
            elif index == len(path) - 1:
                total_time += branch.entry_time
            else:
                total_time += branch.entry_time + branch.transfer_time + branch.dispatch_interval

        return total_time

    def build_preview_text(self):
        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()
        barcode = self.product_combo.currentData()
        quantity = self.quantity_input.value()
        criterion = "time" if self.criterion_combo.currentIndex() == 0 else "cost"
        criterion_label = "Tiempo mínimo" if criterion == "time" else "Costo más bajo"

        if source_id is None or destination_id is None:
            return "Vista previa: seleccione origen y destino"

        if source_id == destination_id:
            return "Vista previa: origen y destino deben ser diferentes"

        if barcode is None:
            return "Vista previa: seleccione un producto"

        source_branch = self.branch_manager.find_by_id(source_id)

        if source_branch is None:
            return "Vista previa: sucursal origen no encontrada"

        product = source_branch.inventory.search_by_barcode(barcode)

        if product is None:
            return "Vista previa: producto no encontrado en la sucursal origen"

        if quantity <= 0:
            return "Vista previa: cantidad inválida"

        if product.stock < quantity:
            return f"Vista previa: stock insuficiente. Disponible: {product.stock}"

        path, selected_weight = self.branch_manager.graph.shortest_path(source_id, destination_id, criterion)

        if not path:
            return "Vista previa: no existe ruta entre las sucursales seleccionadas"

        connection_time, connection_cost = self.get_connection_totals(path)
        internal_time = self.estimate_internal_processing_time(path)
        eta = connection_time + internal_time
        path_text = self.get_path_names_text(path)

        return (
            f"Vista previa ({criterion_label}): {path_text} | "
            f"Tiempo conexión: {connection_time}s | Costo conexión: {connection_cost} | "
            f"Proceso interno: {internal_time}s | ETA estimado: {eta}s | "
            f"Peso usado: {selected_weight}"
        )

    def preview_transfer(self):
        self.result_label.setText(self.build_preview_text())

    def load_branch_options(self):
        branches = self.branch_manager.get_branches()

        self.source_combo.clear()
        self.destination_combo.clear()

        for branch in branches:
            label = self.get_branch_label(branch)
            self.source_combo.addItem(label, branch.id)
            self.destination_combo.addItem(label, branch.id)

        self.load_product_options()
        self.preview_transfer()

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

        self.preview_transfer()

    def execute_transfer(self):
        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()
        barcode = self.product_combo.currentData()
        quantity = self.quantity_input.value()
        criterion = "time" if self.criterion_combo.currentIndex() == 0 else "cost"

        if source_id is None or destination_id is None:
            QMessageBox.warning(self.parent, "Datos incompletos", "Seleccione sucursal origen y destino")
            return

        if barcode is None:
            QMessageBox.warning(self.parent, "Sin producto", "Seleccione un producto para transferir")
            return

        success, message, transfer_request = self.branch_manager.create_transfer_request(
            source_id,
            destination_id,
            barcode,
            quantity,
            criterion
        )
        if success:
            connection_time, connection_cost = self.get_connection_totals(transfer_request.path)
            internal_time = self.estimate_internal_processing_time(transfer_request.path)
            eta = connection_time + internal_time
            transfer_request.set_estimated_total_time(eta)
            transfer_request.start()
        else:
            self.result_label.setText(f"Resultado: {message}")
            QMessageBox.warning(self.parent, "Transferencia no agregada", message)
            return

        path_text = self.get_path_names_text(transfer_request.path)

        result_text = (
            f"Resultado: {message} | Ruta: {path_text} | "
            f"Tiempo conexión: {connection_time}s | Costo conexión: {connection_cost} | "
            f"Proceso interno: {internal_time}s | ETA estimado: {eta}s"
        )
        self.result_label.setText(result_text)
        QMessageBox.information(self.parent, "Transferencia en cola", result_text)