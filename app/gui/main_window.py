from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from app.services.branch_manager import BranchManager
from app.utils.demo_data import load_demo_branches
from app.gui.views.inventory_view import InventoryView
from app.gui.views.graph_view import GraphView
from app.gui.helpers.table_setup import (
    setup_branches_table,
    setup_products_table,
    setup_connections_table,
)


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
            search_input = self.input_product_search,
            start_date_input = self.input_start_date,
            end_date_input = self.input_end_date,
            parent = self
        )

        self.graph_view = GraphView(
            self.branch_manager,
            self.combo_source_branch,
            self.combo_destination_branch,
            self.input_connection_weight,
            self.connections_table,
            result_label=self.label_shortest_path_result,
            parent=self
        )

        setup_branches_table(self.branches_table)
        setup_products_table(self.products_table)
        setup_connections_table(self.connections_table)
        load_demo_branches(self.branch_manager)
        self.inventory_view.refresh_branches_table()
        self.graph_view.load_branch_options()
        self.graph_view.refresh_connections_table()

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
        self.btn_delete_branch = self.findChild(object, "btnDeleteBranch")
        self.btn_delete_product = self.findChild(object, "btnDeleteProduct")
        self.input_product_search = self.findChild(object, "inputProductSearch")
        self.btn_search_product = self.findChild(object, "btnSearchProduct")
        self.btn_clear_product_search = self.findChild(object, "btnClearProductSearch")
        self.input_start_date = self.findChild(object, "inputStartDate")
        self.input_end_date = self.findChild(object, "inputEndDate")
        self.btn_search_by_date_range = self.findChild(object, "btnSearchByDateRange")
        self.btn_clear_date_range = self.findChild(object, "btnClearDateRange")
        self.branches_table = self.findChild(object, "branchesTable")
        self.products_table = self.findChild(object, "productsTable")
        self.pages = self.findChild(object, "pages")

        self.combo_source_branch = self.findChild(object, "comboSourceBranch")
        self.combo_destination_branch = self.findChild(object, "comboDestinationBranch")
        self.input_connection_weight = self.findChild(object, "inputConnectionWeight")
        self.btn_add_connection = self.findChild(object, "btnAddConnection")
        self.connections_table = self.findChild(object, "connectionsTable")
        self.btn_calculate_shortest_path = self.findChild(object, "btnCalculateShortestPath")
        self.label_shortest_path_result = self.findChild(object, "labelShortestPathResult")

        self.btn_view_inventory = self.findChild(object, "btnViewInventory")
        self.btn_view_graph = self.findChild(object, "btnViewGraph")
        self.btn_view_transfers = self.findChild(object, "btnViewTransfers")
        self.btn_view_queues = self.findChild(object, "btnViewQueues")
        self.btn_view_visualizations = self.findChild(object, "btnViewVisualizations")

    def show_graph_view(self):
        self.graph_view.load_branch_options()
        self.graph_view.refresh_connections_table()
        self.pages.setCurrentIndex(1)

    def connect_signals(self):
        self.btn_add_branch.clicked.connect(self.inventory_view.add_branch)
        self.btn_add_product.clicked.connect(self.inventory_view.add_product_to_selected_branch)
        self.btn_delete_branch.clicked.connect(self.inventory_view.delete_selected_branch)
        self.btn_delete_product.clicked.connect(self.inventory_view.delete_selected_product)
        self.btn_search_product.clicked.connect(self.inventory_view.search_products_in_selected_branch)
        self.btn_clear_product_search.clicked.connect(self.inventory_view.clear_product_search)
        self.input_product_search.returnPressed.connect(self.inventory_view.search_products_in_selected_branch)
        self.btn_search_by_date_range.clicked.connect(self.inventory_view.search_products_by_date_range)
        self.btn_clear_date_range.clicked.connect(self.inventory_view.clear_date_range_search)
        self.btn_add_connection.clicked.connect(self.graph_view.add_connection)
        if self.btn_calculate_shortest_path is not None:
            self.btn_calculate_shortest_path.clicked.connect(self.graph_view.calculate_shortest_path)
        self.btn_view_inventory.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.btn_view_graph.clicked.connect(self.show_graph_view)
        self.btn_view_transfers.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        self.btn_view_queues.clicked.connect(lambda: self.pages.setCurrentIndex(3))
        self.btn_view_visualizations.clicked.connect(lambda: self.pages.setCurrentIndex(4))
        self.branches_table.itemSelectionChanged.connect(self.inventory_view.handle_branch_selection)