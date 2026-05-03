from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView, QAbstractItemView
from app.services.inventory_processing_service import InventoryProcessingService


class BenchmarkView:
    def __init__(
        self,
        branch_manager,
        branch_combo,
        input_n,
        input_m,
        result_label,
        results_table=None,
        parent=None
    ):
        self.branch_manager = branch_manager
        self.branch_combo = branch_combo
        self.input_n = input_n
        self.input_m = input_m
        self.result_label = result_label
        self.results_table = results_table
        self.parent = parent
        self.setup_results_table()

    def setup_results_table(self):
        if self.results_table is None:
            return

        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Caso", "Método", "N solicitado", "Consultas", "Productos", "M", "Promedio (μs)"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)

    def load_branch_options(self):
        self.branch_combo.clear()

        for branch in self.branch_manager.get_branches():
            self.branch_combo.addItem(f"{branch.id} - {branch.name}", branch.id)

    def get_selected_branch(self):
        branch_id = self.branch_combo.currentData()

        if branch_id is None:
            return None

        return self.branch_manager.find_by_id(branch_id)

    def get_n(self):
        return self.input_n.value() if self.input_n is not None else 20

    def get_m(self):
        return self.input_m.value() if self.input_m is not None else 5

    def show_result(self, title, message):
        self.result_label.setText(message)
        QMessageBox.information(self.parent, title, message)

    def load_search_results_table(self, results):
        if self.results_table is None:
            return

        self.results_table.setRowCount(len(results))

        for row, result in enumerate(results):
            average_us = result["average_ms"] * 1000

            self.results_table.setItem(row, 0, QTableWidgetItem(result.get("case", "-")))
            self.results_table.setItem(row, 1, QTableWidgetItem(result.get("method", "-")))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(result.get("requested_n", "-"))))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(result.get("executed_queries", "-"))))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(result.get("available_products", "-"))))
            self.results_table.setItem(row, 5, QTableWidgetItem(str(result.get("m", "-"))))
            self.results_table.setItem(row, 6, QTableWidgetItem(f"{average_us:.2f}"))

    def measure_searches(self):
        branch = self.get_selected_branch()

        if branch is None:
            QMessageBox.warning(self.parent, "Datos incompletos", "Seleccione una sucursal")
            return

        results = InventoryProcessingService.benchmark_search_methods(
            branch.inventory,
            self.get_n(),
            self.get_m()
        )
        self.load_search_results_table(results)

        message = (
            f"Búsquedas medidas para {branch.name}. "
            f"N solicitado={self.get_n()}, M={self.get_m()}. "
            "La columna Consultas muestra cuántas búsquedas se ejecutaron realmente por caso."
        )
        self.result_label.setText(message)

    def measure_insertions(self):
        message = (
            "Medición de inserciones pendiente de conectar.\n"
            "Objetivo: medir inserción atomizada en AVL, B, B+, Hash y lista."
        )
        self.show_result("Rendimiento de inserciones", message)

    def measure_deletions(self):
        message = (
            "Medición de eliminaciones pendiente de conectar.\n"
            "Objetivo: medir eliminación propagada en AVL, B, B+, Hash y lista."
        )
        self.show_result("Rendimiento de eliminaciones", message)

    def measure_transfers(self):
        message = (
            "Medición de transferencias pendiente de conectar.\n"
            "Objetivo: comparar rutas calculadas por tiempo mínimo y costo más bajo."
        )
        self.show_result("Rendimiento de transferencias", message)