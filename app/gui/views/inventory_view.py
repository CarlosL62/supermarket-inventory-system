from app.models.branch import Branch
from app.gui.dialogs.add_product_dialog import AddProductDialog
from app.gui.dialogs.add_branch_dialog import AddBranchDialog
from app.gui.helpers.table_loaders import load_branches_table, load_products_table
from PySide6.QtWidgets import QMessageBox


class InventoryView:
    def __init__(self, branch_manager, branches_table, products_table, parent=None):
        self.branch_manager = branch_manager
        self.branches_table = branches_table
        self.products_table = products_table
        self.parent = parent

    def refresh_branches_table(self):
        branches = self.branch_manager.get_branches()
        load_branches_table(self.branches_table, branches)

    def load_products_for_branch(self, branch):
        products = branch.inventory.get_all_products()
        load_products_table(self.products_table, products)

    def get_selected_branch(self):
        selected_items = self.branches_table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        branches = self.branch_manager.get_branches()

        if row < 0 or row >= len(branches):
            return None

        return branches[row]

    def handle_branch_selection(self):
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

        new_id = len(self.branch_manager.get_branches()) + 1
        branch.id = new_id
        self.branch_manager.add_branch(branch)
        self.refresh_branches_table()

        last_row = self.branches_table.rowCount() - 1
        if last_row >= 0:
            self.branches_table.selectRow(last_row)
            self.handle_branch_selection()

    def add_product_to_selected_branch(self):
        branch = self.get_selected_branch()
        if branch is None:
            QMessageBox.warning(self.parent, "Sin sucursal", "Seleccione una sucursal primero.")
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
        self.load_products_for_branch(branch)
        QMessageBox.information(self.parent, "Éxito", "Producto agregado correctamente.")