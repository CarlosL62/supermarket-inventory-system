from PySide6.QtWidgets import QMainWindow, QHeaderView
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from app.services.branch_manager import BranchManager
from app.utils.demo_data import load_demo_branches
from app.gui.views.inventory_view import InventoryView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Inventario de Supermercados")
        self.resize(900, 600)

        self.branch_manager = BranchManager()

        self.load_ui()
        self.bind_ui_elements()

        self.inventory_view = InventoryView(
            self.branch_manager,
            self.branches_table,
            self.products_table,
            parent=self
        )

        self.setup_table()
        self.setup_products_table()
        load_demo_branches(self.branch_manager)
        self.inventory_view.refresh_branches_table()

        self.connect_signals()
        if self.branches_table.rowCount() > 0:
            self.branches_table.selectRow(0)
            self.inventory_view.handle_branch_selection()

    def load_ui(self):
        ui_file = QFile("app/gui/main_window.ui")
        if not ui_file.open(QFile.ReadOnly):
            raise FileNotFoundError("No se pudo abrir main_window.ui")

        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        if self.ui is None:
            raise RuntimeError("No se pudo cargar la interfaz main_window.ui")

        # We load the .ui as a temporary QMainWindow and then take ownership of its central widget
        loaded_size = self.ui.size()
        loaded_title = self.ui.windowTitle()
        central_widget = self.ui.takeCentralWidget()

        if central_widget is None:
            raise RuntimeError("No se pudo obtener el central widget desde main_window.ui")

        self.setCentralWidget(central_widget)
        self.setWindowTitle(loaded_title)
        self.resize(loaded_size)

    def bind_ui_elements(self):
        self.btn_add_branch = self.findChild(object, "btnAddBranch")
        self.btn_add_product = self.findChild(object, "btnAddProduct")
        self.branches_table = self.findChild(object, "branchesTable")
        self.products_table = self.findChild(object, "productsTable")
        self.pages = self.findChild(object, "pages")

        self.btn_view_inventory = self.findChild(object, "btnViewInventory")
        self.btn_view_graph = self.findChild(object, "btnViewGraph")
        self.btn_view_transfers = self.findChild(object, "btnViewTransfers")
        self.btn_view_queues = self.findChild(object, "btnViewQueues")
        self.btn_view_visualizations = self.findChild(object, "btnViewVisualizations")

    def connect_signals(self):
        self.btn_add_branch.clicked.connect(self.inventory_view.add_branch)
        self.btn_add_product.clicked.connect(self.inventory_view.add_product_to_selected_branch)
        self.btn_view_inventory.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.btn_view_graph.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.btn_view_transfers.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        self.btn_view_queues.clicked.connect(lambda: self.pages.setCurrentIndex(3))
        self.btn_view_visualizations.clicked.connect(lambda: self.pages.setCurrentIndex(4))
        self.branches_table.itemSelectionChanged.connect(self.inventory_view.handle_branch_selection)

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
        self.branches_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)