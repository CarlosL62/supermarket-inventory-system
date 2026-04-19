from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from app.services.branch_manager import BranchManager
from app.models.branch import Branch
from app.models.product import Product
from app.gui.dialogs.add_product_dialog import AddProductDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Supermarket Inventory System")
        self.resize(900, 600)

        self.branch_manager = BranchManager()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.btn_add_branch = QPushButton("Agregar sucursal")
        self.btn_add_product = QPushButton("Agregar producto a sucursal")
        self.branches_table = QTableWidget()
        self.products_table = QTableWidget()

        layout.addWidget(self.btn_add_branch)
        layout.addWidget(self.btn_add_product)
        layout.addWidget(self.branches_table)
        layout.addWidget(self.products_table)

        central_widget.setLayout(layout)

        self.setup_table()
        self.setup_products_table()
        self.load_demo_data()
        self.refresh_table()

        self.btn_add_branch.clicked.connect(self.add_branch)
        self.btn_add_product.clicked.connect(self.add_product_to_selected_branch)
        self.branches_table.itemSelectionChanged.connect(self.on_branch_selected)
        if self.branches_table.rowCount() > 0:
            self.branches_table.selectRow(0)
            self.on_branch_selected()

    def setup_products_table(self):
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            "Nombre", "Código", "Categoría",
            "Fecha", "Marca", "Precio", "Stock"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


    def setup_table(self):
        self.branches_table.setColumnCount(7)
        self.branches_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Ubicación",
            "Tiempo ingreso", "Tiempo traspaso", "Intervalo despacho",
            "Cantidad productos"
        ])

    def load_demo_data(self):
        self.branch_manager.add_branch(Branch(1, "Central", "Zona 1", 5, 3, 10))
        self.branch_manager.add_branch(Branch(2, "Norte", "Zona 5", 4, 2, 8))

        branch1 = self.branch_manager.get_branches()[0]
        branch1.inventory.add_product(Product("Leche", "1234567890123", "Lacteos", "2026-01-15", "LaVaquita", 12.50, 20))
        branch1.inventory.add_product(Product("Pan", "9876543210000", "Panaderia", "2026-01-10", "Bimbo", 8.00, 35))

        branch2 = self.branch_manager.get_branches()[1]
        branch2.inventory.add_product(Product("Queso", "1112223334445", "Lacteos", "2026-02-01", "Cremoso", 25.75, 10))

    def refresh_table(self):
        branches = self.branch_manager.get_branches()
        self.branches_table.setRowCount(len(branches))

        for i, branch in enumerate(branches):
            self.branches_table.setItem(i, 0, QTableWidgetItem(str(branch.id)))
            self.branches_table.setItem(i, 1, QTableWidgetItem(branch.name))
            self.branches_table.setItem(i, 2, QTableWidgetItem(branch.location))
            self.branches_table.setItem(i, 3, QTableWidgetItem(str(branch.entry_time)))
            self.branches_table.setItem(i, 4, QTableWidgetItem(str(branch.transfer_time)))
            self.branches_table.setItem(i, 5, QTableWidgetItem(str(branch.dispatch_interval)))
            self.branches_table.setItem(i, 6, QTableWidgetItem(str(len(branch.inventory.get_all_products()))))

    def add_branch(self):
        new_id = len(self.branch_manager.get_branches()) + 1
        self.branch_manager.add_branch(
            Branch(new_id, "Nueva sucursal", "Pendiente", 0, 0, 0)
        )
        self.refresh_table()
        last_row = self.branches_table.rowCount() - 1
        if last_row >= 0:
            self.branches_table.selectRow(last_row)
            self.on_branch_selected()

    def get_selected_branch(self):
        selected_items = self.branches_table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        branches = self.branch_manager.get_branches()

        if row < 0 or row >= len(branches):
            return None

        return branches[row]

    def add_product_to_selected_branch(self):
        branch = self.get_selected_branch()
        if branch is None:
            QMessageBox.warning(self, "Sin sucursal", "Seleccione una sucursal primero.")
            return

        dialog = AddProductDialog(self)
        if not dialog.exec():
            return

        product = dialog.get_product()
        if product is None:
            return

        success = branch.inventory.add_product(product)

        if not success:
            QMessageBox.warning(self, "Duplicado", "Ya existe un producto con ese código de barras en esta sucursal.")
            return

        self.refresh_table()
        self.load_products(branch)
        QMessageBox.information(self, "Éxito", "Producto agregado correctamente.")

    def on_branch_selected(self):
        branch = self.get_selected_branch()
        if branch is None:
            self.products_table.setRowCount(0)
            return

        self.load_products(branch)

    def load_products(self, branch):
        products = branch.inventory.get_all_products()
        self.products_table.setRowCount(len(products))

        for i, product in enumerate(products):
            self.products_table.setItem(i, 0, QTableWidgetItem(product.name))
            self.products_table.setItem(i, 1, QTableWidgetItem(product.barcode))
            self.products_table.setItem(i, 2, QTableWidgetItem(product.category))
            self.products_table.setItem(i, 3, QTableWidgetItem(product.expiry_date))
            self.products_table.setItem(i, 4, QTableWidgetItem(product.brand))
            self.products_table.setItem(i, 5, QTableWidgetItem(str(product.price)))
            self.products_table.setItem(i, 6, QTableWidgetItem(str(product.stock)))