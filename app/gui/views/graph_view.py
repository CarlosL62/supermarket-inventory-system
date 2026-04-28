from PySide6.QtWidgets import QMessageBox
from app.gui.helpers.table_loaders import load_connections_table


class GraphView:
    def __init__(self, branch_manager, source_combo, destination_combo, weight_input, cost_input, bidirectional_checkbox, connections_table, result_label=None, parent=None):
        self.branch_manager = branch_manager
        self.source_combo = source_combo
        self.destination_combo = destination_combo
        self.weight_input = weight_input
        self.cost_input = cost_input
        self.bidirectional_checkbox = bidirectional_checkbox
        self.connections_table = connections_table
        self.result_label = result_label
        self.parent = parent

    def get_branch_label(self, branch_id):
        for branch in self.branch_manager.get_branches():
            if branch.id == branch_id:
                return f"{branch.id} - {branch.name}"

        return str(branch_id)

    def load_branch_options(self):
        branches = self.branch_manager.get_branches()

        self.source_combo.clear()
        self.destination_combo.clear()

        for branch in branches:
            label = f"{branch.id} - {branch.name}"
            self.source_combo.addItem(label, branch.id)
            self.destination_combo.addItem(label, branch.id)

    def refresh_connections_table(self):
        rows = []

        for source_id, destination_id, time_weight, cost_weight in self.branch_manager.graph.get_all_connections():
            source_label = self.get_branch_label(source_id)
            destination_label = self.get_branch_label(destination_id)
            weight_label = f"Tiempo: {time_weight} | Costo: {cost_weight}"
            rows.append((source_label, destination_label, weight_label))

        load_connections_table(self.connections_table, rows)

    def add_connection(self):
        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()
        weight = self.weight_input.value()
        cost = self.cost_input.value()
        bidirectional = self.bidirectional_checkbox.isChecked()

        if source_id is None or destination_id is None:
            QMessageBox.warning(self.parent, "Datos incompletos", "Seleccione ambas sucursales")
            return

        if source_id == destination_id:
            QMessageBox.warning(self.parent, "Conexión inválida", "No puede conectar una sucursal consigo misma")
            return

        success = self.branch_manager.connect_branches(source_id, destination_id, weight, cost, bidirectional)
        if not success:
            QMessageBox.warning(self.parent, "Duplicado", "La conexión ya existe")
            return

        self.refresh_connections_table()
        QMessageBox.information(self.parent, "Éxito", "Conexión agregada correctamente")

    def calculate_shortest_path(self):
        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()

        if source_id is None or destination_id is None:
            QMessageBox.warning(self.parent, "Datos incompletos", "Seleccione ambas sucursales")
            return

        if source_id == destination_id:
            QMessageBox.warning(self.parent, "Ruta inválida", "Seleccione sucursales diferentes")
            return

        path, total_weight = self.branch_manager.graph.shortest_path(source_id, destination_id)

        if not path:
            message = "No existe una ruta entre las sucursales seleccionadas"
            if self.result_label is not None:
                self.result_label.setText(f"Ruta: {message}")
            QMessageBox.warning(self.parent, "Sin ruta", message)
            return

        path_labels = [self.get_branch_label(branch_id) for branch_id in path]
        path_text = " -> ".join(path_labels)
        result_text = f"Ruta: {path_text} | Peso total: {total_weight}"

        if self.result_label is not None:
            self.result_label.setText(result_text)

        QMessageBox.information(self.parent, "Ruta más corta", result_text)