from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer
from app.services.branch_manager import BranchManager
from app.utils.demo_data import load_demo_branches
from app.gui.views.inventory_view import InventoryView
from app.gui.views.graph_view import GraphView
from app.gui.views.transfer_view import TransferView
from app.gui.views.queue_view import QueueView
from app.gui.views.visualization_view import VisualizationView
from app.gui.helpers.table_setup import (
    setup_branches_table,
    setup_products_table,
    setup_connections_table,
    setup_transfer_queue_table,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Inventario de Supermercados")
        self.resize(900, 600)

        # BranchManager acts as the central point for branches, graph, inventory, and transfers
        self.branch_manager = BranchManager()

        self.load_ui()
        self.bind_ui_elements()

        self.inventory_view = InventoryView(
            self.branch_manager,
            self.branches_table,
            self.products_table,
            search_input=self.input_product_search,
            start_date_input=self.input_start_date,
            end_date_input=self.input_end_date,
            parent=self
        )

        self.graph_view = GraphView(
            self.branch_manager,
            self.combo_source_branch,
            self.combo_destination_branch,
            self.input_connection_weight,
            self.input_connection_cost,
            self.check_bidirectional_connection,
            self.graph_graphics_view,
            self.connections_table,
            result_label=self.label_shortest_path_result,
            parent=self
        )

        self.transfer_view = TransferView(
            self.branch_manager,
            self.combo_transfer_source_branch,
            self.combo_transfer_destination_branch,
            self.combo_transfer_product,
            self.input_transfer_quantity,
            self.combo_transfer_criterion,
            self.label_transfer_result,
            parent=self
        )

        self.queue_view = QueueView(
            self.branch_manager,
            self.transfer_queue_table,
            self.label_queue_result,
            parent=self
        )

        self.visualization_view = VisualizationView(
            self.branch_manager,
            self.combo_visualization_branch,
            self.combo_visualization_structure,
            self.btn_refresh_visualization,
            self.tree_graphics_view,
            self.label_visualization_result,
            parent=self
        )

        # Tables are configured before loading data to avoid empty or incorrectly formatted views
        setup_branches_table(self.branches_table)
        setup_products_table(self.products_table)
        setup_connections_table(self.connections_table)
        setup_transfer_queue_table(self.transfer_queue_table)
        load_demo_branches(self.branch_manager)
        self.inventory_view.refresh_branches_table()
        self.graph_view.load_branch_options()
        self.graph_view.refresh_connections_table()
        self.transfer_view.load_branch_options()
        self.queue_view.refresh_queue_table()

        self.visualization_view.load_branch_options()

        self.connect_signals()
        if self.branches_table.rowCount() > 0:
            self.branches_table.selectRow(0)
            self.inventory_view.handle_branch_selection()

        # Main simulation timer: advances pending transfers once per second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(1000)

    def load_ui(self):
        ui_file = QFile("app/gui/main_window.ui")
        if not ui_file.open(QFile.ReadOnly):
            raise FileNotFoundError("No se pudo abrir main_window.ui")

        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        if self.ui is None:
            raise RuntimeError("No se pudo cargar la interfaz main_window.ui")

        # The .ui is loaded as a temporary window, then its central widget is reused by this class
        loaded_size = self.ui.size()
        loaded_title = self.ui.windowTitle()
        central_widget = self.ui.takeCentralWidget()

        if central_widget is None:
            raise RuntimeError("No se pudo obtener el central widget desde main_window.ui")

        self.setCentralWidget(central_widget)
        self.setWindowTitle(loaded_title)
        self.resize(loaded_size)

    def bind_ui_elements(self):
        # Inventory screen widgets
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

        # Branch network and route comparison widgets
        self.combo_source_branch = self.findChild(object, "comboSourceBranch")
        self.combo_destination_branch = self.findChild(object, "comboDestinationBranch")
        self.input_connection_weight = self.findChild(object, "inputConnectionWeight")
        self.input_connection_cost = self.findChild(object, "inputConnectionCost")
        self.check_bidirectional_connection = self.findChild(object, "checkBidirectionalConnection")
        self.btn_add_connection = self.findChild(object, "btnAddConnection")
        self.connections_table = self.findChild(object, "connectionsTable")
        self.graph_graphics_view = self.findChild(object, "graphGraphicsView")
        self.btn_calculate_shortest_path = self.findChild(object, "btnCalculateShortestPath")
        self.label_shortest_path_result = self.findChild(object, "labelShortestPathResult")

        # Transfer and dispatch queue widgets
        self.combo_transfer_source_branch = self.findChild(object, "comboTransferSourceBranch")
        self.combo_transfer_destination_branch = self.findChild(object, "comboTransferDestinationBranch")
        self.combo_transfer_product = self.findChild(object, "comboTransferProduct")
        self.input_transfer_quantity = self.findChild(object, "inputTransferQuantity")
        self.combo_transfer_criterion = self.findChild(object, "comboTransferCriterion")
        self.btn_execute_transfer = self.findChild(object, "btnExecuteTransfer")
        self.label_transfer_result = self.findChild(object, "labelTransferResult")
        self.label_queue_result = self.findChild(object, "labelQueueResult")
        self.transfer_queue_table = self.findChild(object, "transferQueueTable")

        # Structure visualization widgets
        self.combo_visualization_branch = self.findChild(object, "comboVisualizationBranch")
        self.combo_visualization_structure = self.findChild(object, "comboVisualizationStructure")
        self.btn_refresh_visualization = self.findChild(object, "btnRefreshVisualization")
        self.label_visualization_result = self.findChild(object, "labelVisualizationResult")
        self.tree_graphics_view = self.findChild(object, "treeGraphicsView")

        # Sidebar buttons used to navigate between modules
        self.btn_view_inventory = self.findChild(object, "btnViewInventory")
        self.btn_view_graph = self.findChild(object, "btnViewGraph")
        self.btn_view_transfers = self.findChild(object, "btnViewTransfers")
        self.btn_view_queues = self.findChild(object, "btnViewQueues")
        self.btn_view_visualizations = self.findChild(object, "btnViewVisualizations")

    def show_graph_view(self):
        self.pages.setCurrentIndex(1)
        self.graph_view.load_branch_options()
        self.graph_view.refresh_connections_table()

    def show_transfer_view(self):
        # Reload branches and products so transfers use updated data
        self.transfer_view.load_branch_options()
        self.pages.setCurrentIndex(2)

    def show_queue_view(self):
        self.queue_view.refresh_queue_table()
        self.pages.setCurrentIndex(3)

    def show_visualization_view(self):
        self.visualization_view.load_branch_options()
        self.pages.setCurrentIndex(4)

    def show_inventory_view(self):
        # Refresh on entry because branches may have changed from the inventory screen
        self.pages.setCurrentIndex(0)

    def update_simulation(self):
        # The simulation is based on the FIFO queue of pending transfers
        transfers = self.branch_manager.get_pending_transfers()

        for transfer in transfers:
            if transfer.status == "Pendiente":
                transfer.start()

            if transfer.remaining_time == 0 and not transfer.completed:
                current_branch_id = transfer.path[transfer.current_index]
                current_branch = self.branch_manager.find_by_id(current_branch_id)

                if current_branch is None:
                    continue

                # When a stage ends, calculate the next time and stage name based on the branch role
                if transfer.current_index == 0:
                    time_cost = current_branch.dispatch_interval
                    stage_name = "En cola de salida"
                elif transfer.current_index == len(transfer.path) - 1:
                    time_cost = current_branch.entry_time
                    stage_name = "En cola de ingreso"
                else:
                    time_cost = (
                        current_branch.entry_time +
                        current_branch.transfer_time +
                        current_branch.dispatch_interval
                    )
                    stage_name = "En preparación de traspaso"

                transfer.set_step_time(time_cost, stage_name)

            transfer.tick()

        # Stock is moved only when the transfer reaches its final destination
        self.branch_manager.apply_completed_transfers()

        if transfers:
            self.queue_view.refresh_queue_table()

    def connect_signals(self):
        # Connect interface events to each module action
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
        self.combo_transfer_source_branch.currentIndexChanged.connect(self.transfer_view.load_product_options)
        self.btn_execute_transfer.clicked.connect(self.transfer_view.execute_transfer)
        self.btn_refresh_visualization.clicked.connect(self.visualization_view.render_tree)
        self.btn_view_inventory.clicked.connect(self.show_inventory_view)
        self.btn_view_graph.clicked.connect(self.show_graph_view)
        self.btn_view_transfers.clicked.connect(self.show_transfer_view)
        self.btn_view_queues.clicked.connect(self.show_queue_view)
        self.btn_view_visualizations.clicked.connect(self.show_visualization_view)
        self.branches_table.itemSelectionChanged.connect(self.inventory_view.handle_branch_selection)
