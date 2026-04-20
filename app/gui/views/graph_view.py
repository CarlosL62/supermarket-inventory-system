from PySide6.QtWidgets import QMessageBox
from app.gui.helpers.table_loaders import load_connections_table


class GraphView:
    def __init__(self, branch_manager, source_combo, destination_combo, weight_input, connections_table, parent=None):
        self.branch_manager = branch_manager
        self.source_combo = source_combo
        self.destination_combo = destination_combo
        self.weight_input = weight_input
        self.connections_table = connections_table
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

        for source_id, destination_id, weight in self.branch_manager.graph.get_all_connections():
            source_label = self.get_branch_label(source_id)
            destination_label = self.get_branch_label(destination_id)
            rows.append((source_label, destination_label, weight))

        load_connections_table(self.connections_table, rows)

    def add_connection(self):
        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()
        weight = self.weight_input.value()

        if source_id is None or destination_id is None:
            QMessageBox.warning(self.parent, "Datos incompletos", "Seleccione ambas sucursales")
            return

        if source_id == destination_id:
            QMessageBox.warning(self.parent, "Conexión inválida", "No puede conectar una sucursal consigo misma")
            return

        success = self.branch_manager.connect_branches(source_id, destination_id, weight)
        if not success:
            QMessageBox.warning(self.parent, "Duplicado", "La conexión ya existe")
            return

        self.refresh_connections_table()
        QMessageBox.information(self.parent, "Éxito", "Conexión agregada correctamente")