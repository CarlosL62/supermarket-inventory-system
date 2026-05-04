from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtSvg import QSvgRenderer
from app.gui.helpers.table_loaders import load_transfer_queue_table
from app.utils.graphviz_renderer import build_branch_graph_svg


class QueueView:
    def __init__(self, branch_manager, transfers_table, result_label, route_graphics_view=None, parent=None):
        self.branch_manager = branch_manager
        self.transfers_table = transfers_table
        self.result_label = result_label
        self.route_graphics_view = route_graphics_view
        self.parent = parent
        self.route_scene = QGraphicsScene() if route_graphics_view is not None else None
        self.route_svg_renderer = None
        self.route_svg_item = None

        self.setup_route_graphics_view()
        self.transfers_table.itemSelectionChanged.connect(self.handle_transfer_selection)

    def setup_route_graphics_view(self):
        if self.route_graphics_view is None:
            return

        self.route_graphics_view.setScene(self.route_scene)
        self.route_graphics_view.setMinimumHeight(300)
        self.route_graphics_view.setBackgroundBrush(QBrush(QColor("#eef2f7")))
        self.route_scene.setBackgroundBrush(QBrush(QColor("#eef2f7")))
        self.route_graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.route_graphics_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.route_graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.route_graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def refresh_queue_table(self):
        selected_transfer = self.get_selected_transfer()
        pending_transfers = self.branch_manager.get_pending_transfers()
        load_transfer_queue_table(self.transfers_table, pending_transfers, self.branch_manager)

        if selected_transfer is not None:
            self.restore_selected_transfer(selected_transfer)
            self.render_selected_transfer_route(selected_transfer)

    def restore_selected_transfer(self, selected_transfer):
        for row in range(self.transfers_table.rowCount()):
            first_item = self.transfers_table.item(row, 0)

            if first_item is None:
                continue

            transfer_request = first_item.data(Qt.ItemDataRole.UserRole)

            if transfer_request is selected_transfer:
                self.transfers_table.selectRow(row)
                return

    def get_selected_transfer(self):
        selected_items = self.transfers_table.selectedItems()

        if not selected_items:
            return None

        return selected_items[0].data(Qt.ItemDataRole.UserRole)

    def render_selected_transfer_route(self, transfer_request):
        if self.route_graphics_view is None or self.route_scene is None:
            return

        self.route_scene.clear()
        self.route_svg_renderer = None
        self.route_svg_item = None

        if not transfer_request.path:
            self.route_scene.addText("No existe ruta para visualizar")
            return

        criterion = transfer_request.criterion
        highlighted_time_path = transfer_request.path if criterion == "time" else None
        highlighted_cost_path = transfer_request.path if criterion == "cost" else None
        current_branch_id = transfer_request.get_current_branch_id()

        svg_data = build_branch_graph_svg(
            self.branch_manager.get_branches(),
            self.branch_manager.get_connections(),
            highlighted_time_path=highlighted_time_path,
            highlighted_cost_path=highlighted_cost_path,
            current_branch_id=current_branch_id
        )

        svg_bytes = svg_data.encode("utf-8") if isinstance(svg_data, str) else svg_data
        self.route_svg_renderer = QSvgRenderer(QByteArray(svg_bytes))

        if not self.route_svg_renderer.isValid():
            self.route_scene.addText("No se pudo renderizar la ruta")
            return

        self.route_svg_item = QGraphicsSvgItem()
        self.route_svg_item.setSharedRenderer(self.route_svg_renderer)
        self.route_scene.addItem(self.route_svg_item)
        self.route_scene.setSceneRect(self.route_svg_item.boundingRect())
        self.route_graphics_view.fitInView(
            self.route_scene.sceneRect(),
            Qt.AspectRatioMode.KeepAspectRatio
        )

    def handle_transfer_selection(self):
        transfer_request = self.get_selected_transfer()

        if transfer_request is None:
            return

        if self.result_label is not None:
            self.result_label.setText(
                f"Transferencia seleccionada: {transfer_request.current_stage} | "
                f"Ruta: {transfer_request.get_path_text()} | "
                f"Ubicación actual: {transfer_request.get_current_branch_id()}"
            )

        self.render_selected_transfer_route(transfer_request)

        if self.parent is None or not hasattr(self.parent, "graph_view"):
            return

        self.parent.graph_view.render_transfer_route(
            transfer_request.path,
            criterion=transfer_request.criterion,
            current_branch_id=transfer_request.get_current_branch_id(),
            result_prefix="Ruta de transferencia seleccionada"
        )