from PySide6.QtWidgets import QMessageBox, QGraphicsScene, QGraphicsView
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtSvg import QSvgRenderer
from app.gui.helpers.transfer_worker import TransferWorker
from app.utils.graphviz_renderer import build_branch_graph_svg


class TransferView:
    def __init__(self, branch_manager, source_combo, destination_combo, product_combo, quantity_input, criterion_combo, result_label, route_graphics_view=None, parent=None):
        self.branch_manager = branch_manager
        self.source_combo = source_combo
        self.destination_combo = destination_combo
        self.product_combo = product_combo
        self.quantity_input = quantity_input
        self.criterion_combo = criterion_combo
        self.result_label = result_label
        self.route_graphics_view = route_graphics_view
        self.route_scene = QGraphicsScene() if route_graphics_view is not None else None
        self.route_svg_renderer = None
        self.route_svg_item = None
        self.parent = parent
        self.transfer_workers = []

        self.setup_route_graphics_view()

        self.source_combo.currentIndexChanged.connect(self.preview_transfer)
        self.destination_combo.currentIndexChanged.connect(self.preview_transfer)
        self.product_combo.currentIndexChanged.connect(self.preview_transfer)
        self.quantity_input.valueChanged.connect(self.preview_transfer)
        self.criterion_combo.currentIndexChanged.connect(self.preview_transfer)

    def setup_route_graphics_view(self):
        if self.route_graphics_view is None:
            return

        self.route_graphics_view.setScene(self.route_scene)
        self.route_graphics_view.setMinimumHeight(320)
        self.route_graphics_view.setBackgroundBrush(QBrush(QColor("#eef2f7")))
        self.route_scene.setBackgroundBrush(QBrush(QColor("#eef2f7")))
        self.route_graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.route_graphics_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.route_graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.route_graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def render_route_preview_graph(self, path, criterion="time"):
        if self.route_graphics_view is None or self.route_scene is None:
            return

        self.route_scene.clear()
        self.route_svg_renderer = None
        self.route_svg_item = None

        if not path:
            self.route_scene.addText("No existe ruta para visualizar")
            return

        highlighted_time_path = path if criterion == "time" else None
        highlighted_cost_path = path if criterion == "cost" else None

        svg_data = build_branch_graph_svg(
            self.branch_manager.get_branches(),
            self.branch_manager.get_connections(),
            highlighted_time_path=highlighted_time_path,
            highlighted_cost_path=highlighted_cost_path
        )

        if isinstance(svg_data, str):
            svg_bytes = svg_data.encode("utf-8")
        else:
            svg_bytes = svg_data

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

    def get_branch_label(self, branch):
        return f"{branch.id} - {branch.name}"

    def get_branch_name(self, branch_id):
        branch = self.branch_manager.find_by_id(branch_id)
        return branch.name if branch is not None else str(branch_id)

    def get_path_names_text(self, path):
        return " -> ".join(self.get_branch_name(branch_id) for branch_id in path)

    def get_connection_totals(self, path):
        total_time = 0
        total_cost = 0

        if not path:
            return total_time, total_cost

        for index in range(len(path) - 1):
            source_id = path[index]
            destination_id = path[index + 1]

            for neighbor_id, time_weight, cost_weight in self.branch_manager.graph.get_neighbors(source_id):
                if neighbor_id == destination_id:
                    total_time += time_weight
                    total_cost += cost_weight
                    break

        return total_time, total_cost

    def estimate_internal_processing_time(self, path):
        total_time = 0

        for index, branch_id in enumerate(path):
            branch = self.branch_manager.find_by_id(branch_id)

            if branch is None:
                continue

            if index == 0:
                total_time += branch.dispatch_interval
            elif index == len(path) - 1:
                total_time += branch.entry_time
            else:
                total_time += branch.entry_time + branch.transfer_time + branch.dispatch_interval

        return total_time

    def get_connection_time(self, source_id, destination_id):
        for neighbor_id, time_weight, cost_weight in self.branch_manager.graph.get_neighbors(source_id):
            if neighbor_id == destination_id:
                return time_weight

        return 0

    def build_simulation_steps(self, path):
        steps = []

        if not path:
            return steps

        for index, branch_id in enumerate(path):
            branch = self.branch_manager.find_by_id(branch_id)

            if branch is None:
                continue

            is_origin = index == 0
            is_destination = index == len(path) - 1

            if is_origin:
                steps.append({
                    "branch_id": branch_id,
                    "stage": "Cola de salida",
                    "duration": branch.dispatch_interval,
                    "description": "Producto listo para salir desde la sucursal origen"
                })
            else:
                steps.append({
                    "branch_id": branch_id,
                    "stage": "Cola de ingreso",
                    "duration": branch.entry_time,
                    "description": "Producto recibido y procesado por la sucursal"
                })

            if not is_destination:
                next_branch_id = path[index + 1]

                if not is_origin:
                    steps.append({
                        "branch_id": branch_id,
                        "stage": "Cola de preparación de traspaso",
                        "duration": branch.transfer_time,
                        "description": "Sucursal intermedia prepara el producto para continuar la ruta"
                    })

                    steps.append({
                        "branch_id": branch_id,
                        "stage": "Cola de salida",
                        "duration": branch.dispatch_interval,
                        "description": "Sucursal intermedia despacha el producto hacia la siguiente sucursal"
                    })

                connection_time = self.get_connection_time(branch_id, next_branch_id)
                steps.append({
                    "branch_id": branch_id,
                    "stage": f"En tránsito hacia {self.get_branch_name(next_branch_id)}",
                    "duration": connection_time,
                    "description": "Producto viajando por la conexión seleccionada"
                })

        return steps

    def calculate_transfer_timing(self, path):
        connection_time, connection_cost = self.get_connection_totals(path)
        simulation_steps = self.build_simulation_steps(path)
        eta = sum(step.get("duration", 0) for step in simulation_steps)
        internal_time = eta - connection_time

        return connection_time, connection_cost, internal_time, eta, simulation_steps

    def build_preview_text(self):
        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()
        barcode = self.product_combo.currentData()
        quantity = self.quantity_input.value()
        criterion = "time" if self.criterion_combo.currentIndex() == 0 else "cost"
        criterion_label = "Tiempo mínimo" if criterion == "time" else "Costo más bajo"

        if source_id is None or destination_id is None:
            return "Vista previa: seleccione origen y destino"

        if source_id == destination_id:
            return "Vista previa: origen y destino deben ser diferentes"

        if barcode is None:
            return "Vista previa: seleccione un producto"

        source_branch = self.branch_manager.find_by_id(source_id)

        if source_branch is None:
            return "Vista previa: sucursal origen no encontrada"

        product = source_branch.inventory.search_by_barcode(barcode)

        if product is None:
            return "Vista previa: producto no encontrado en la sucursal origen"

        if quantity <= 0:
            return "Vista previa: cantidad inválida"

        if product.stock < quantity:
            return f"Vista previa: stock insuficiente. Disponible: {product.stock}"

        path, selected_weight = self.branch_manager.graph.shortest_path(source_id, destination_id, criterion)

        if not path:
            return "Vista previa: no existe ruta entre las sucursales seleccionadas"

        connection_time, connection_cost, internal_time, eta, _ = self.calculate_transfer_timing(path)
        path_text = self.get_path_names_text(path)

        return (
            f"Vista previa ({criterion_label}): {path_text} | "
            f"Tiempo conexión: {connection_time}s | Costo conexión: {connection_cost} | "
            f"Proceso interno: {internal_time}s | ETA estimado: {eta}s | "
            f"Peso usado: {selected_weight}"
        )

    def preview_transfer_route_on_graph(self):
        if self.parent is None or not hasattr(self.parent, "graph_view"):
            return

        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()
        barcode = self.product_combo.currentData()
        criterion = "time" if self.criterion_combo.currentIndex() == 0 else "cost"

        if source_id is None or destination_id is None or barcode is None:
            return

        if source_id == destination_id:
            return

        path, _ = self.branch_manager.graph.shortest_path(source_id, destination_id, criterion)

        if not path:
            return

        self.render_route_preview_graph(path, criterion)

        self.parent.graph_view.render_transfer_route(
            path,
            criterion=criterion,
            result_prefix="Vista previa de transferencia"
        )

    def preview_transfer(self):
        self.result_label.setText(self.build_preview_text())
        self.preview_transfer_route_on_graph()

    def load_branch_options(self):
        branches = self.branch_manager.get_branches()

        self.source_combo.clear()
        self.destination_combo.clear()

        for branch in branches:
            label = self.get_branch_label(branch)
            self.source_combo.addItem(label, branch.id)
            self.destination_combo.addItem(label, branch.id)

        self.load_product_options()
        self.preview_transfer()

    def load_product_options(self):
        self.product_combo.clear()

        source_id = self.source_combo.currentData()
        if source_id is None:
            return

        source_branch = self.branch_manager.find_by_id(source_id)
        if source_branch is None:
            return

        for product in source_branch.inventory.get_all_products():
            label = f"{product.name} - {product.barcode} - Stock: {product.stock}"
            self.product_combo.addItem(label, product.barcode)

        self.preview_transfer()

    def start_transfer_worker(self, transfer_request):
        worker = TransferWorker(transfer_request, self.branch_manager)
        # Reserve the first queue ticket before the thread starts so FIFO
        # follows creation order instead of thread scheduling order.
        worker.reserve_current_queue_ticket()
        worker.updated.connect(self.handle_transfer_worker_update)
        worker.finished.connect(lambda transfer_request, finished_worker=worker: self.handle_transfer_worker_finished(
            transfer_request,
            finished_worker
        ))
        self.transfer_workers.append(worker)
        worker.start()

    def handle_transfer_worker_update(self, transfer_request):
        if self.parent is not None and hasattr(self.parent, "queue_view"):
            self.parent.queue_view.refresh_queue_table()

    def handle_transfer_worker_finished(self, transfer_request, finished_worker):
        if finished_worker in self.transfer_workers:
            self.transfer_workers.remove(finished_worker)

        finished_worker.deleteLater()

        if self.parent is not None and hasattr(self.parent, "queue_view"):
            self.parent.queue_view.refresh_queue_table()

    def stop_all_workers(self):
        for worker in list(self.transfer_workers):
            worker.stop()

        for worker in list(self.transfer_workers):
            worker.wait()

    def execute_transfer(self):
        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()
        barcode = self.product_combo.currentData()
        quantity = self.quantity_input.value()
        criterion = "time" if self.criterion_combo.currentIndex() == 0 else "cost"

        if source_id is None or destination_id is None:
            QMessageBox.warning(self.parent, "Datos incompletos", "Seleccione sucursal origen y destino")
            return

        if barcode is None:
            QMessageBox.warning(self.parent, "Sin producto", "Seleccione un producto para transferir")
            return

        success, message, transfer_request = self.branch_manager.create_transfer_request(
            source_id,
            destination_id,
            barcode,
            quantity,
            criterion
        )
        if success:
            connection_time, connection_cost, internal_time, eta, simulation_steps = self.calculate_transfer_timing(
                transfer_request.path
            )
            transfer_request.set_estimated_total_time(eta)
            transfer_request.configure_simulation_steps(simulation_steps)
            transfer_request.start()
            self.start_transfer_worker(transfer_request)
            self.render_route_preview_graph(transfer_request.path, criterion)
            if self.parent is not None and hasattr(self.parent, "graph_view"):
                self.parent.graph_view.render_transfer_route(
                    transfer_request.path,
                    criterion=criterion,
                    current_branch_id=transfer_request.get_current_branch_id(),
                    result_prefix="Transferencia en ejecución"
                )
        else:
            self.result_label.setText(f"Resultado: {message}")
            QMessageBox.warning(self.parent, "Transferencia no agregada", message)
            return

        path_text = self.get_path_names_text(transfer_request.path)

        result_text = (
            f"Resultado: {message} | Ruta: {path_text} | "
            f"Tiempo conexión: {connection_time}s | Costo conexión: {connection_cost} | "
            f"Proceso interno: {internal_time}s | ETA estimado: {eta}s"
        )
        self.result_label.setText(result_text)
        QMessageBox.information(self.parent, "Transferencia en cola", result_text)
