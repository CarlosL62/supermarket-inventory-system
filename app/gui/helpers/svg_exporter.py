from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QFileDialog, QMessageBox


def export_svg(svg_data, parent, default_name="export.svg"):
    if not svg_data:
        QMessageBox.warning(parent, "Sin contenido", "No hay contenido SVG para exportar")
        return

    file_path, selected_filter = QFileDialog.getSaveFileName(
        parent,
        "Exportar SVG",
        default_name,
        "SVG Files (*.svg);;PNG Files (*.png)"
    )

    if not file_path:
        return

    svg_bytes = svg_data if isinstance(svg_data, bytes) else svg_data.encode("utf-8")
    svg_text = svg_data.decode("utf-8") if isinstance(svg_data, bytes) else svg_data

    try:
        if selected_filter.startswith("PNG") or file_path.lower().endswith(".png"):
            if not file_path.lower().endswith(".png"):
                file_path += ".png"

            renderer = QSvgRenderer(QByteArray(svg_bytes))
            svg_size = renderer.defaultSize()

            if not renderer.isValid() or svg_size.width() <= 0 or svg_size.height() <= 0:
                raise RuntimeError("El SVG no tiene dimensiones válidas para exportar")

            scale_factor = 4
            margin = 80
            width = svg_size.width() * scale_factor + margin * 2
            height = svg_size.height() * scale_factor + margin * 2

            image = QImage(width, height, QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)

            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            target_rect = QRectF(
                margin,
                margin,
                svg_size.width() * scale_factor,
                svg_size.height() * scale_factor
            )
            renderer.render(painter, target_rect)
            painter.end()

            if not image.save(file_path):
                raise RuntimeError("No se pudo guardar la imagen PNG")
        else:
            if not file_path.lower().endswith(".svg"):
                file_path += ".svg"

            with open(file_path, "w", encoding="utf-8") as svg_file:
                svg_file.write(svg_text)

        QMessageBox.information(parent, "Exportación completada", f"Archivo guardado en:\n{file_path}")

    except Exception as error:
        QMessageBox.critical(parent, "Error al exportar", f"No se pudo exportar el archivo:\n{error}")
