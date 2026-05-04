from app.gui.dialogs.add_branch_dialog import AddBranchDialog
from app.gui.dialogs.add_product_dialog import AddProductDialog
from app.gui.helpers.table_loaders import load_branches_table, load_products_table
from app.services.inventory_processing_service import InventoryProcessingService
from PySide6.QtWidgets import QMessageBox


class InventoryView:
    def __init__(self, branch_manager, branches_table, products_table, search_input=None, start_date_input=None, end_date_input=None, parent=None):
        self.branch_manager = branch_manager
        self.branches_table = branches_table
        self.products_table = products_table
        self.search_input = search_input
        self.start_date_input = start_date_input
        self.end_date_input = end_date_input
        self.date_range_filter_active = False
        self.parent = parent

    def get_selected_branch_products(self):
        branch = self.require_selected_branch()
        if branch is None:
            return None, []

        return branch, branch.inventory.get_all_products()


    def search_products_with_metrics(self, method="sequential"):
        branch, products = self.get_selected_branch_products()
        if branch is None:
            return

        if self.search_input is None:
            return

        query = self.search_input.text().strip()
        if not query:
            self.load_products_for_branch(branch)
            return

        found_products, elapsed_ms = InventoryProcessingService.search_products(
            products,
            query,
            method,
            inventory=branch.inventory
        )

        search_labels = {
            "name": "nombre",
            "barcode": "código de barras",
            "category": "categoría",
            "sequential": "secuencial",
            "binary": "binaria por nombre",
            "hash": "hash por código"
        }
        search_label = search_labels.get(method, method)

        elapsed_us = elapsed_ms * 1000
        message = (
            f"Búsqueda por {search_label} | "
            f"Coincidencias: {len(found_products)} | "
            f"Tiempo: {elapsed_us:.2f} μs"
        )

        load_products_table(self.products_table, found_products)
        QMessageBox.information(self.parent, "Métrica de búsqueda", message)


    def get_selected_product_barcode(self):
        selected_items = self.products_table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        barcode_item = self.products_table.item(row, 1)

        if barcode_item is None:
            return None

        return barcode_item.text()

    def require_selected_product_barcode(self):
        barcode = self.get_selected_product_barcode()
        if barcode is None:
            QMessageBox.warning(self.parent, "Sin producto", "Seleccione un producto primero")
            return None
        return barcode

    def refresh_branches_table(self):
        branches = self.branch_manager.get_branches()
        load_branches_table(self.branches_table, branches)

    def load_products_for_branch(self, branch):
        products = branch.inventory.get_all_products()
        load_products_table(self.products_table, products)

    def reset_text_search(self):
        if self.search_input is not None:
            self.search_input.clear()

    def reset_date_range_filter(self):
        self.date_range_filter_active = False

        if self.start_date_input is not None:
            self.start_date_input.clear()
        if self.end_date_input is not None:
            self.end_date_input.clear()

    def reset_all_filters(self):
        self.reset_text_search()
        self.reset_date_range_filter()

    def search_products_by_date_range(self):
        branch = self.require_selected_branch()
        if branch is None:
            return

        if self.start_date_input is None or self.end_date_input is None:
            return

        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")

        if start_date > end_date:
            QMessageBox.warning(self.parent, "Rango inválido", "La fecha inicial no puede ser mayor que la fecha final")
            return

        self.date_range_filter_active = True

        products = branch.inventory.search_by_expiry_date_range(start_date, end_date)
        load_products_table(self.products_table, products)

    def clear_date_range_search(self):
        self.reset_date_range_filter()

        branch = self.get_selected_branch()
        if branch is None:
            self.products_table.setRowCount(0)
            return

        self.load_products_for_branch(branch)

    def search_products_in_selected_branch(self):
        self.search_products_with_metrics("name")

    def search_products_by_name(self):
        self.search_products_with_metrics("name")

    def search_products_by_barcode(self):
        self.search_products_with_metrics("barcode")

    def search_products_by_category(self):
        self.search_products_with_metrics("category")

    def clear_product_search(self):
        self.reset_all_filters()

        branch = self.get_selected_branch()
        if branch is None:
            self.products_table.setRowCount(0)
            return

        self.load_products_for_branch(branch)

    def get_selected_branch(self):
        selected_items = self.branches_table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        branches = self.branch_manager.get_branches()

        if row < 0 or row >= len(branches):
            return None

        return branches[row]

    def require_selected_branch(self):
        branch = self.get_selected_branch()
        if branch is None:
            QMessageBox.warning(self.parent, "Sin sucursal", "Seleccione una sucursal primero")
            return None
        return branch

    def handle_branch_selection(self):
        if self.search_input is not None and self.search_input.text().strip():
            self.search_products_in_selected_branch()
            return

        if self.date_range_filter_active:
            self.search_products_by_date_range()
            return

        branch = self.get_selected_branch()
        if branch is None:
            self.products_table.setRowCount(0)
            return

        self.load_products_for_branch(branch)

    def add_branch(self):
        dialog = AddBranchDialog(self.parent)
        if not dialog.exec():
            return

        branch = dialog.get_branch()
        if branch is None:
            return

        self.branch_manager.add_branch(branch)
        self.refresh_branches_table()

        last_row = self.branches_table.rowCount() - 1
        if last_row >= 0:
            self.branches_table.selectRow(last_row)
            self.handle_branch_selection()

    def delete_selected_branch(self):
        branch = self.require_selected_branch()
        if branch is None:
            return

        confirmation = QMessageBox.question(
            self.parent,
            "Eliminar sucursal",
            f"¿Está seguro de eliminar la sucursal '{branch.name}'?"
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        success = self.branch_manager.delete_branch(branch.id)
        if not success:
            QMessageBox.warning(self.parent, "Error", "No se pudo eliminar la sucursal")
            return

        self.refresh_branches_table()
        self.products_table.setRowCount(0)

        self.reset_all_filters()

        if self.branches_table.rowCount() > 0:
            self.branches_table.selectRow(0)
            self.handle_branch_selection()

    def add_product_to_selected_branch(self):
        branch = self.require_selected_branch()
        if branch is None:
            return

        dialog = AddProductDialog(self.parent)
        if not dialog.exec():
            return

        product = dialog.get_product()
        if product is None:
            return

        success = branch.inventory.add_product(product)

        if not success:
            QMessageBox.warning(self.parent, "Duplicado", "Ya existe un producto con ese código de barras en esta sucursal.")
            return

        self.refresh_branches_table()

        self.reset_all_filters()

        self.load_products_for_branch(branch)

        QMessageBox.information(self.parent, "Éxito", "Producto agregado correctamente.")

    def delete_selected_product(self):
        branch = self.require_selected_branch()
        if branch is None:
            return

        barcode = self.require_selected_product_barcode()
        if barcode is None:
            return

        confirmation = QMessageBox.question(
            self.parent,
            "Eliminar producto",
            f"¿Está seguro de eliminar el producto con código {barcode}?"
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        success = branch.inventory.delete_product_by_barcode(barcode)

        if not success:
            QMessageBox.warning(self.parent, "Error", "No se pudo eliminar el producto")
            return

        self.refresh_branches_table()

        self.reset_all_filters()

        self.load_products_for_branch(branch)
        QMessageBox.information(self.parent, "Éxito", "Producto eliminado correctamente")
