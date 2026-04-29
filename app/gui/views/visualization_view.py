from PySide6.QtWidgets import QMessageBox, QGraphicsScene, QGraphicsView
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtSvg import QSvgRenderer
from graphviz.backend import ExecutableNotFound
from app.utils.graphviz_renderer import build_binary_tree_svg, build_multiway_tree_svg


class VisualizationView:
    def __init__(self, branch_manager, branch_combo, structure_combo, refresh_button, graphics_view, result_label, parent=None):
        self.branch_manager = branch_manager
        self.branch_combo = branch_combo
        self.structure_combo = structure_combo
        self.refresh_button = refresh_button
        self.graphics_view = graphics_view
        self.result_label = result_label
        self.parent = parent
        self.scene = QGraphicsScene()
        self.current_svg_item = None
        self.current_svg_renderer = None
        self.zoom_factor = 1.0
        self.min_zoom_factor = 0.35
        self.max_zoom_factor = 6.0
        self.scene_padding = 24

        self.graphics_view.setScene(self.scene)
        self.graphics_view.setMinimumHeight(560)
        self.graphics_view.setBackgroundBrush(QBrush(QColor("#eef2f7")))
        self.scene.setBackgroundBrush(QBrush(QColor("#eef2f7")))
        self.graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.graphics_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.graphics_view.wheelEvent = self.handle_wheel
        self.graphics_view.resizeEvent = self.handle_resize

    def handle_resize(self, event):
        self.fit_visualization()
        event.accept()

    def handle_wheel(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        next_zoom = self.zoom_factor * factor

        if next_zoom < self.min_zoom_factor or next_zoom > self.max_zoom_factor:
            event.accept()
            return

        self.zoom_factor = next_zoom
        self.graphics_view.scale(factor, factor)
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
        root = self.find_tree_root(branch.inventory, structure_name)
        title = f"{structure_name} - {branch.name}"

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
        self.zoom_factor = 1.0

        try:
            svg_data = self.build_tree_svg(branch, structure_name)
            self.current_svg_renderer = QSvgRenderer(QByteArray(svg_data))

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