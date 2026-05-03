from PySide6.QtWidgets import QFileDialog, QMessageBox
from app.utils.csv_loader import CSVLoader


class CSVView:
    def __init__(
        self,
        branch_manager,
        branches_input,
        connections_input,
        products_input,
        select_branches_button,
        select_connections_button,
        select_products_button,
        load_button,
        errors_text,
        result_label,
        refresh_callback=None,
        parent=None
    ):
        self.branch_manager = branch_manager
        self.branches_input = branches_input
        self.connections_input = connections_input
        self.products_input = products_input
        self.select_branches_button = select_branches_button
        self.select_connections_button = select_connections_button
        self.select_products_button = select_products_button
        self.load_button = load_button
        self.errors_text = errors_text
        self.result_label = result_label
        self.refresh_callback = refresh_callback
        self.parent = parent
        self.csv_loader = CSVLoader()

        self.connect_signals()
        self.load_error_log()

    def connect_signals(self):
        if self.select_branches_button is not None:
            self.select_branches_button.clicked.connect(self.select_branches_file)

        if self.select_connections_button is not None:
            self.select_connections_button.clicked.connect(self.select_connections_file)

        if self.select_products_button is not None:
            self.select_products_button.clicked.connect(self.select_products_file)

        if self.load_button is not None:
            self.load_button.clicked.connect(self.load_csv_files)

    def select_file(self, title):
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            title,
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        return file_path

    def select_branches_file(self):
        file_path = self.select_file("Seleccionar CSV de sucursales")
        if file_path:
            self.branches_input.setText(file_path)

    def select_connections_file(self):
        file_path = self.select_file("Seleccionar CSV de conexiones")
        if file_path:
            self.connections_input.setText(file_path)

    def select_products_file(self):
        file_path = self.select_file("Seleccionar CSV de productos")
        if file_path:
            self.products_input.setText(file_path)

    def load_error_log(self):
        if self.errors_text is None:
            return

        try:
            with open(self.csv_loader.error_log_path, "r", encoding="utf-8") as error_file:
                self.errors_text.setPlainText(error_file.read())
        except FileNotFoundError:
            self.errors_text.setPlainText("Aún no hay archivo errors.log")

    def load_csv_files(self):
        branches_file = self.branches_input.text().strip()
        connections_file = self.connections_input.text().strip()
        products_file = self.products_input.text().strip()

        if not branches_file or not connections_file or not products_file:
            QMessageBox.warning(
                self.parent,
                "Archivos incompletos",
                "Seleccione los CSV de sucursales, conexiones y productos"
            )
            return

        result = self.csv_loader.load_all(
            branches_file,
            connections_file,
            products_file,
            self.branch_manager
        )

        message = (
            f"Carga finalizada | "
            f"Sucursales: {result['branches']} | "
            f"Conexiones: {result['connections']} | "
            f"Productos: {result['products']} | "
            f"Errores: {result['error_log']}"
        )

        self.result_label.setText(message)
        self.load_error_log()

        if self.refresh_callback is not None:
            self.refresh_callback()

        QMessageBox.information(self.parent, "Carga CSV", message)