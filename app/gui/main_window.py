from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from app.services.branch_manager import BranchManager
from app.models.branch import Branch
from app.models.product import Product


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
        self.branches_table = QTableWidget()

        layout.addWidget(self.btn_add_branch)
        layout.addWidget(self.branches_table)

        central_widget.setLayout(layout)

        self.setup_table()
        self.load_demo_data()
        self.refresh_table()

        self.btn_add_branch.clicked.connect(self.add_branch)

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