from PySide6.QtWidgets import QMessageBox, QGraphicsScene, QGraphicsView, QFileDialog
from PySide6.QtGui import QBrush, QColor, QImage, QPainter
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtSvg import QSvgRenderer
from graphviz.backend import ExecutableNotFound
from app.utils.graphviz_renderer import build_binary_tree_svg, build_multiway_tree_svg, build_hash_table_svg


class VisualizationView:
    def __init__(self, branch_manager, branch_combo, structure_combo, refresh_button, export_button, zoom_in_button, zoom_out_button, reset_zoom_button, graphics_view, result_label, parent=None):
        self.branch_manager = branch_manager
        self.branch_combo = branch_combo
        self.structure_combo = structure_combo
        self.refresh_button = refresh_button
        self.export_button = export_button
        self.zoom_in_button = zoom_in_button
        self.zoom_out_button = zoom_out_button
        self.reset_zoom_button = reset_zoom_button
        self.graphics_view = graphics_view
        self.result_label = result_label
        self.parent = parent
        self.scene = QGraphicsScene()
        self.current_svg_item = None
        self.current_svg_renderer = None
        self.zoom_factor = 1.0
        self.min_zoom_factor = 0.005
        self.max_zoom_factor = 200.0
        self.scene_padding = 24
        self.current_svg_data = None

        self.graphics_view.setScene(self.scene)
        self.graphics_view.setMinimumHeight(560)
        self.graphics_view.setBackgroundBrush(QBrush(QColor("#eef2f7")))
        self.scene.setBackgroundBrush(QBrush(QColor("#eef2f7")))
        self.graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.graphics_view.setInteractive(True)
        self.graphics_view.setMouseTracking(True)
        self.graphics_view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.graphics_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.graphics_view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.graphics_view.wheelEvent = self.handle_wheel
        self.graphics_view.resizeEvent = self.handle_resize
        if self.export_button is not None:
            self.export_button.clicked.connect(self.export_visualization)
        if self.zoom_in_button is not None:
            self.zoom_in_button.clicked.connect(self.zoom_in)
        if self.zoom_out_button is not None:
            self.zoom_out_button.clicked.connect(self.zoom_out)
        if self.reset_zoom_button is not None:
            self.reset_zoom_button.clicked.connect(self.reset_zoom)

    def get_svg_bytes(self):
        if self.current_svg_data is None:
            return None

        if isinstance(self.current_svg_data, bytes):
            return self.current_svg_data

        return self.current_svg_data.encode("utf-8")

    def get_svg_text(self):
        if self.current_svg_data is None:
            return ""

        if isinstance(self.current_svg_data, bytes):
            return self.current_svg_data.decode("utf-8")

        return self.current_svg_data

    def handle_resize(self, event):
        if self.current_svg_item is not None and self.zoom_factor == 1.0:
            self.fit_visualization()
        event.accept()

    def apply_zoom(self, factor):
        if self.current_svg_item is None:
            return

        next_zoom = self.zoom_factor * factor

        if next_zoom < self.min_zoom_factor:
            factor = self.min_zoom_factor / self.zoom_factor
            self.zoom_factor = self.min_zoom_factor
        elif next_zoom > self.max_zoom_factor:
            factor = self.max_zoom_factor / self.zoom_factor
            self.zoom_factor = self.max_zoom_factor
        else:
            self.zoom_factor = next_zoom

        self.graphics_view.scale(factor, factor)
        self.result_label.setText(f"Zoom: {self.zoom_factor * 100:.0f}%")

    def zoom_in(self):
        self.apply_zoom(1.25)

    def zoom_out(self):
        self.apply_zoom(0.8)

    def reset_zoom(self):
        self.fit_visualization()
        self.result_label.setText("Zoom: 100%")

    def handle_wheel(self, event):
        delta = event.angleDelta().y()

        if delta == 0:
            event.accept()
            return

        self.apply_zoom(1.25 if delta > 0 else 0.8)
        event.accept()

    def update_scene_rect(self):
        if self.current_svg_item is None:
            return

        rect = self.current_svg_item.mapToScene(self.current_svg_item.boundingRect()).boundingRect()
        self.scene.setSceneRect(
            rect.adjusted(
                -self.scene_padding,
                -self.scene_padding,
                self.scene_padding,
                self.scene_padding
            )
        )

    def fit_visualization(self):
        if self.current_svg_item is None:
            return

        self.update_scene_rect()
        self.graphics_view.resetTransform()
        self.graphics_view.fitInView(
            self.scene.sceneRect(),
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.zoom_factor = 1.0

    def load_branch_options(self):
        self.branch_combo.clear()

        for branch in self.branch_manager.get_branches():
            self.branch_combo.addItem(f"{branch.id} - {branch.name}", branch.id)

    def find_selected_branch(self):
        branch_id = self.branch_combo.currentData()

        if branch_id is None:
            return None

        return self.branch_manager.find_by_id(branch_id)

    def find_tree_root(self, inventory, structure_name):
        if structure_name == "Hash Table":
            return getattr(inventory, "hash_table", None)
        if structure_name == "AVL":
            candidates = [
                "avl_tree", "name_tree", "product_name_tree", "products_by_name",
                "tree_by_name", "avl", "root"
            ]
        elif structure_name == "B Tree":
            candidates = [
                "b_tree", "expiration_tree", "expiry_tree", "products_by_expiry",
                "date_tree", "btree"
            ]
        else:
            candidates = [
                "b_plus_tree", "bplus_tree", "category_tree", "products_by_category",
                "b_plus", "bplustree"
            ]

        for attr in candidates:
            if not hasattr(inventory, attr):
                continue

            tree = getattr(inventory, attr)

            if hasattr(tree, "root"):
                return tree.root

            return tree

        return None

    def build_tree_svg(self, branch, structure_name):
        title = f"{structure_name} - {branch.name}"
        if structure_name == "Hash Table":
            hash_table = self.find_tree_root(branch.inventory, structure_name)
            return build_hash_table_svg(hash_table, title=title)
        root = self.find_tree_root(branch.inventory, structure_name)

        if structure_name == "AVL":
            return build_binary_tree_svg(
                root,
                title=title,
                value_fields=("key", "name", "product_name", "barcode")
            )

        if structure_name == "B Tree":
            return build_multiway_tree_svg(
                root,
                title=title,
                value_fields=("expiration_date", "expiry_date", "expiration", "date")
            )

        return build_multiway_tree_svg(
            root,
            title=title,
            value_fields=("category", "name", "product_name"),
            show_leaf_links=True
        )

    def render_tree(self):
        branch = self.find_selected_branch()
        structure_name = self.structure_combo.currentText()

        if branch is None:
            QMessageBox.warning(self.parent, "Datos incompletos", "Seleccione una sucursal")
            return

        self.scene.clear()
        self.current_svg_item = None
        self.current_svg_renderer = None
        self.current_svg_data = None
        self.zoom_factor = 1.0

        try:
            svg_data = self.build_tree_svg(branch, structure_name)
            self.current_svg_data = svg_data
            self.current_svg_renderer = QSvgRenderer(QByteArray(self.get_svg_bytes()))

            if not self.current_svg_renderer.isValid():
                raise RuntimeError("El SVG generado por Graphviz no es válido")

            svg_item = QGraphicsSvgItem()
            svg_item.setSharedRenderer(self.current_svg_renderer)
            svg_item.setScale(1.0)
            self.scene.addItem(svg_item)
            self.current_svg_item = svg_item
            self.fit_visualization()
            self.result_label.setText(f"Visualizando {structure_name} de {branch.name}")

        except ExecutableNotFound:
            self.scene.addText("Graphviz no está instalado en el sistema. En macOS use: brew install graphviz")
        except Exception as error:
            self.scene.addText(f"No se pudo renderizar la estructura: {error}")
            self.result_label.setText("No se pudo renderizar la estructura seleccionada")

    def export_visualization(self):
        if not self.current_svg_data:
            QMessageBox.warning(self.parent, "Sin visualización", "Primero genere una visualización")
            return

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.parent,
            "Exportar visualización",
            "visualizacion.svg",
            "SVG Files (*.svg);;PNG Files (*.png)"
        )

        if not file_path:
            return

        try:
            if selected_filter.startswith("PNG") or file_path.lower().endswith(".png"):
                if not file_path.lower().endswith(".png"):
                    file_path += ".png"

                renderer = QSvgRenderer(QByteArray(self.get_svg_bytes()))
                size = renderer.defaultSize()
                image = QImage(size.width(), size.height(), QImage.Format.Format_ARGB32)
                image.fill(Qt.GlobalColor.white)

                painter = QPainter(image)
                renderer.render(painter)
                painter.end()
                image.save(file_path)
            else:
                if not file_path.lower().endswith(".svg"):
                    file_path += ".svg"

                with open(file_path, "w", encoding="utf-8") as svg_file:
                    svg_file.write(self.get_svg_text())

            QMessageBox.information(self.parent, "Exportación completada", f"Archivo guardado en:\n{file_path}")

        except Exception as error:
            QMessageBox.critical(self.parent, "Error al exportar", f"No se pudo exportar la visualización:\n{error}")