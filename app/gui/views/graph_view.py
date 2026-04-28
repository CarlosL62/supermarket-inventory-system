from PySide6.QtWidgets import QMessageBox, QGraphicsScene, QGraphicsView, QSizePolicy
from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtCore import Qt, QByteArray, QTimer
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtSvg import QSvgRenderer
from graphviz import Digraph
from graphviz.backend import ExecutableNotFound
from app.gui.helpers.table_loaders import load_connections_table


class GraphView:
    def __init__(self, branch_manager, source_combo, destination_combo, weight_input, cost_input, bidirectional_checkbox, graphics_view, connections_table, result_label=None, parent=None):
        self.branch_manager = branch_manager
        self.source_combo = source_combo
        self.destination_combo = destination_combo
        self.weight_input = weight_input
        self.cost_input = cost_input
        self.bidirectional_checkbox = bidirectional_checkbox
        self.graphics_view = graphics_view
        self.connections_table = connections_table
        self.result_label = result_label
        self.parent = parent
        self.scene = QGraphicsScene()
        self.current_svg_item = None
        self.current_svg_renderer = None
        self.base_scale = 1.0
        self.zoom_factor = 1.0
        self.zoom_step = 1.15
        self.min_zoom_factor = 0.35
        self.max_zoom_factor = 6.0
        self.scene_padding = 24
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setMinimumHeight(420)
        self.connections_table.setMinimumHeight(170)
        self.connections_table.setMaximumHeight(260)
        self.graphics_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.connections_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.graphics_view.setBackgroundBrush(QBrush(QColor("#eef2f7")))
        self.scene.setBackgroundBrush(QBrush(QColor("#eef2f7")))
        self.graphics_view.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
        )
        self.graphics_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.graphics_view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.graphics_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._default_wheel_event = self.graphics_view.wheelEvent
        self._default_resize_event = self.graphics_view.resizeEvent
        self.graphics_view.wheelEvent = self.handle_graph_wheel
        self.graphics_view.resizeEvent = self.handle_graph_resize
        graph_layout = self.graphics_view.parentWidget().layout() if self.graphics_view.parentWidget() else None
        if graph_layout is not None:
            graph_layout.setStretch(graph_layout.indexOf(self.graphics_view), 5)
            graph_layout.setStretch(graph_layout.indexOf(self.connections_table), 2)

    def handle_graph_resize(self, event):
        self._default_resize_event(event)
        self.fit_graph_image(reset_zoom=False)

    def handle_graph_wheel(self, event):
        if self.current_svg_item is None:
            self._default_wheel_event(event)
            return

        zoom_direction = event.angleDelta().y()
        if zoom_direction == 0:
            event.ignore()
            return

        step_factor = self.zoom_step if zoom_direction > 0 else 1 / self.zoom_step
        next_zoom = max(
            self.min_zoom_factor,
            min(self.zoom_factor * step_factor, self.max_zoom_factor)
        )
        applied_factor = next_zoom / self.zoom_factor

        if abs(applied_factor - 1.0) < 1e-6:
            event.accept()
            return

        self.zoom_factor = next_zoom
        self.graphics_view.scale(applied_factor, applied_factor)

        event.accept()

    def get_branch_label(self, branch_id):
        for branch in self.branch_manager.get_branches():
            if branch.id == branch_id:
                return f"{branch.id} - {branch.name}"

        return str(branch_id)

    def load_branch_options(self):
        branches = self.branch_manager.get_branches()

        self.source_combo.clear()
        self.destination_combo.clear()

        for branch in branches:
            label = f"{branch.id} - {branch.name}"
            self.source_combo.addItem(label, branch.id)
            self.destination_combo.addItem(label, branch.id)

        self.draw_graph()

    def refresh_connections_table(self):
        rows = []

        for source_id, destination_id, time_weight, cost_weight, is_bidirectional in self.branch_manager.graph.get_all_connections():
            source_label = self.get_branch_label(source_id)
            destination_label = self.get_branch_label(destination_id)
            direction_label = "Bidireccional" if is_bidirectional else "Unidireccional"
            weight_label = f"{direction_label} | Tiempo: {time_weight} | Costo: {cost_weight}"
            rows.append((source_label, destination_label, weight_label))

        load_connections_table(self.connections_table, rows)
        self.draw_graph()

    def build_graphviz_diagram(self):
        dot = Digraph("branch_graph", format="svg")
        dot.attr(
            rankdir="LR",
            bgcolor="#eef2f7",
            splines="spline",
            overlap="false",
            nodesep="0.45",
            ranksep="0.65",
            ratio="compress",
            margin="0",
            pad="0.0",
            fontname="Arial"
        )

        dot.attr(
            "node",
            shape="circle",
            style="filled",
            fillcolor="#dbeafe",
            color="#0f172a",
            fontcolor="#111827",
            fontname="Arial",
            fontsize="11",
            width="1.0",
            fixedsize="true"
        )

        dot.attr(
            "edge",
            color="#1f2937",
            fontcolor="#111827",
            fontname="Arial",
            fontsize="10",
            penwidth="2"
        )

        for branch in self.branch_manager.get_branches():
            label = f"{branch.id}\n{branch.name}"
            dot.node(str(branch.id), label)

        for source_id, destination_id, time_weight, cost_weight, is_bidirectional in self.branch_manager.graph.get_all_connections():
            label = f"T:{time_weight} | C:{cost_weight}"

            if is_bidirectional:
                dot.edge(
                    str(source_id),
                    str(destination_id),
                    label=label,
                    dir="both",
                    color="#2563eb",
                    fontcolor="#111827",
                    fontname="Arial"
                )
            else:
                dot.edge(
                    str(source_id),
                    str(destination_id),
                    label=label,
                    dir="forward",
                    color="#1f2937",
                    fontcolor="#111827",
                    fontname="Arial"
                )

        return dot

    def update_scene_rect(self):
        if self.current_svg_item is None:
            return

        scene_rect = self.current_svg_item.mapRectToScene(
            self.current_svg_item.boundingRect()
        )
        padded_rect = scene_rect.adjusted(
            -self.scene_padding,
            -self.scene_padding,
            self.scene_padding,
            self.scene_padding
        )
        self.scene.setSceneRect(padded_rect)

    def fit_graph_image(self, reset_zoom=True):
        if self.current_svg_item is None:
            return

        svg_rect = self.current_svg_item.boundingRect()
        viewport_rect = self.graphics_view.viewport().rect()

        if svg_rect.isEmpty() or viewport_rect.isEmpty():
            return

        if viewport_rect.width() < 32 or viewport_rect.height() < 32:
            QTimer.singleShot(0, lambda: self.fit_graph_image(reset_zoom=reset_zoom))
            return

        available_width = max(1, viewport_rect.width() - (self.scene_padding * 2))
        available_height = max(1, viewport_rect.height() - (self.scene_padding * 2))

        self.base_scale = min(
            available_width / svg_rect.width(),
            available_height / svg_rect.height()
        ) * 0.96
        self.current_svg_item.setScale(max(self.base_scale, 0.01))
        self.update_scene_rect()
        self.graphics_view.resetTransform()

        if reset_zoom:
            self.zoom_factor = 1.0

        self.graphics_view.scale(self.zoom_factor, self.zoom_factor)
        self.graphics_view.centerOn(self.current_svg_item)

    def draw_graph(self):
        if self.graphics_view is None:
            return

        self.scene.clear()
        self.current_svg_item = None
        self.current_svg_renderer = None
        self.graphics_view.resetTransform()
        self.zoom_factor = 1.0

        try:
            dot = self.build_graphviz_diagram()
            svg_data = dot.pipe(format="svg")
            svg_renderer = QSvgRenderer(QByteArray(svg_data))

            if not svg_renderer.isValid():
                raise RuntimeError("No se pudo cargar el SVG generado por Graphviz")

            svg_item = QGraphicsSvgItem()
            svg_item.setSharedRenderer(svg_renderer)
            svg_rect = svg_item.boundingRect()

            if svg_rect.isEmpty():
                raise RuntimeError("El SVG generado por Graphviz no tiene un tamano valido")

            self.scene.addItem(svg_item)
            self.current_svg_item = svg_item
            self.current_svg_renderer = svg_renderer
            self.fit_graph_image(reset_zoom=True)

        except ImportError:
            text_item = self.scene.addText("Graphviz no está instalado en Python. Instale con: pip install graphviz")
            self.scene.setSceneRect(text_item.sceneBoundingRect().adjusted(-12, -12, 12, 12))
        except ExecutableNotFound:
            text_item = self.scene.addText("Graphviz no está instalado en el sistema. En macOS use: brew install graphviz")
            self.scene.setSceneRect(text_item.sceneBoundingRect().adjusted(-12, -12, 12, 12))
        except Exception as error:
            text_item = self.scene.addText(f"No se pudo renderizar el grafo: {error}")
            self.scene.setSceneRect(text_item.sceneBoundingRect().adjusted(-12, -12, 12, 12))

    def add_connection(self):
        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()
        weight = self.weight_input.value()
        cost = self.cost_input.value()
        bidirectional = self.bidirectional_checkbox.isChecked()

        if source_id is None or destination_id is None:
            QMessageBox.warning(self.parent, "Datos incompletos", "Seleccione ambas sucursales")
            return

        if source_id == destination_id:
            QMessageBox.warning(self.parent, "Conexión inválida", "No puede conectar una sucursal consigo misma")
            return

        success = self.branch_manager.connect_branches(source_id, destination_id, weight, cost, bidirectional)
        if not success:
            QMessageBox.warning(self.parent, "Duplicado", "La conexión ya existe")
            return

        self.refresh_connections_table()
        QMessageBox.information(self.parent, "Éxito", "Conexión agregada correctamente")

    def calculate_shortest_path(self):
        source_id = self.source_combo.currentData()
        destination_id = self.destination_combo.currentData()

        if source_id is None or destination_id is None:
            QMessageBox.warning(self.parent, "Datos incompletos", "Seleccione ambas sucursales")
            return

        if source_id == destination_id:
            QMessageBox.warning(self.parent, "Ruta inválida", "Seleccione sucursales diferentes")
            return

        path, total_weight = self.branch_manager.graph.shortest_path(source_id, destination_id)

        if not path:
            message = "No existe una ruta entre las sucursales seleccionadas"
            if self.result_label is not None:
                self.result_label.setText(f"Ruta: {message}")
            QMessageBox.warning(self.parent, "Sin ruta", message)
            return

        path_labels = [self.get_branch_label(branch_id) for branch_id in path]
        path_text = " -> ".join(path_labels)
        result_text = f"Ruta: {path_text} | Peso total: {total_weight}"

        if self.result_label is not None:
            self.result_label.setText(result_text)

        QMessageBox.information(self.parent, "Ruta más corta", result_text)
