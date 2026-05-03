import csv
import os
from app.models.branch import Branch
from app.models.product import Product

DEFAULT_ERROR_LOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "errors.log")
)


class CSVLoader:
    def __init__(self, error_log_path=None):
        self.error_log_path = error_log_path or DEFAULT_ERROR_LOG_PATH
        os.makedirs(os.path.dirname(self.error_log_path), exist_ok=True)
        self.clear_errors()

    def clear_errors(self):
        with open(self.error_log_path, "w", encoding="utf-8") as error_file:
            error_file.write("Registro de errores CSV\n")
            error_file.write("=======================\n")
            error_file.write("El archivo se reinicia al abrir la aplicación o iniciar una nueva carga.\n\n")

    def log_file_section(self, title, file_path):
        with open(self.error_log_path, "a", encoding="utf-8") as error_file:
            error_file.write(f"\n--- {title} ---\n")
            error_file.write(f"Archivo: {file_path}\n")

    def log_error(self, file_path, line_number, message):
        with open(self.error_log_path, "a", encoding="utf-8") as error_file:
            error_file.write(f"  Línea {line_number}: {message}\n")

    def validate_file(self, file_path):
        if not file_path:
            return False, "Ruta de archivo vacía"

        if not os.path.exists(file_path):
            return False, "El archivo no existe"

        if not os.path.isfile(file_path):
            return False, "La ruta no corresponde a un archivo"

        if not os.access(file_path, os.R_OK):
            return False, "El archivo no tiene permisos de lectura"

        return True, "Archivo válido"

    def read_rows(self, file_path):
        is_valid, message = self.validate_file(file_path)

        if not is_valid:
            self.log_error(file_path, 0, message)
            return []

        try:
            with open(file_path, newline="", encoding="utf-8-sig") as csv_file:
                reader = csv.reader(
                    csv_file,
                    delimiter=",",
                    quotechar='"',
                    skipinitialspace=True
                )
                return list(reader)
        except Exception as error:
            self.log_error(file_path, 0, f"No se pudo leer el archivo: {error}")
            return []

    def parse_int(self, value, field_name):
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"{field_name} debe ser entero")

    def parse_float(self, value, field_name):
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{field_name} debe ser numérico")

    def is_valid_barcode(self, barcode):
        return barcode.isdigit() and len(barcode) == 10

    def load_branches(self, file_path, branch_manager):
        self.log_file_section("SUCURSALES", file_path)
        rows = self.read_rows(file_path)
        loaded_count = 0

        for line_number, row in enumerate(rows, start=1):
            if line_number == 1 and row and row[0].strip().lower() in ("id", "sucursalid"):
                continue

            try:
                if len(row) != 6:
                    raise ValueError("Formato esperado: ID, Nombre, Ubicación, t_ingreso, t_traspaso, t_despacho")

                branch_id = self.parse_int(row[0].strip(), "ID")
                name = row[1].strip()
                location = row[2].strip()
                entry_time = self.parse_int(row[3].strip(), "t_ingreso")
                transfer_time = self.parse_int(row[4].strip(), "t_traspaso")
                dispatch_interval = self.parse_int(row[5].strip(), "t_despacho")

                if not name:
                    raise ValueError("Nombre de sucursal vacío")

                if branch_manager.find_by_id(branch_id) is not None:
                    raise ValueError(f"Sucursal duplicada con ID {branch_id}")

                branch_manager.add_branch(
                    Branch(branch_id, name, location, entry_time, transfer_time, dispatch_interval)
                )
                loaded_count += 1

            except Exception as error:
                self.log_error(file_path, line_number, str(error))

        return loaded_count

    def load_connections(self, file_path, branch_manager):
        self.log_file_section("CONEXIONES", file_path)
        rows = self.read_rows(file_path)
        loaded_count = 0

        for line_number, row in enumerate(rows, start=1):
            if line_number == 1 and row and row[0].strip().lower() in ("origenid", "origen"):
                continue

            try:
                if len(row) not in (4, 5):
                    raise ValueError("Formato esperado: OrigenID, DestinoID, Tiempo, Costo[, Bidireccional]")

                source_id = self.parse_int(row[0].strip(), "OrigenID")
                destination_id = self.parse_int(row[1].strip(), "DestinoID")
                time_weight = self.parse_int(row[2].strip(), "Tiempo")
                cost_weight = self.parse_int(row[3].strip(), "Costo")
                is_bidirectional = True

                if len(row) == 5:
                    bidirectional_value = row[4].strip().lower()
                    is_bidirectional = bidirectional_value in ("1", "true", "si", "sí", "yes", "y")

                if branch_manager.find_by_id(source_id) is None:
                    raise ValueError(f"Sucursal origen no existe: {source_id}")

                if branch_manager.find_by_id(destination_id) is None:
                    raise ValueError(f"Sucursal destino no existe: {destination_id}")

                branch_manager.connect_branches(
                    source_id,
                    destination_id,
                    time_weight,
                    cost_weight,
                    is_bidirectional
                )
                loaded_count += 1

            except Exception as error:
                self.log_error(file_path, line_number, str(error))

        return loaded_count

    def collect_existing_barcodes(self, branch_manager):
        existing_barcodes = set()

        for branch in branch_manager.get_branches():
            for product in branch.inventory.get_all_products():
                existing_barcodes.add(product.barcode)

        return existing_barcodes

    def load_products(self, file_path, branch_manager):
        self.log_file_section("PRODUCTOS", file_path)
        rows = self.read_rows(file_path)
        loaded_count = 0
        existing_barcodes = self.collect_existing_barcodes(branch_manager)

        for line_number, row in enumerate(rows, start=1):
            if line_number == 1 and row and row[0].strip().lower() in ("sucursalid", "sucursal"):
                continue

            try:
                if len(row) != 8:
                    raise ValueError(
                        "Formato esperado: SucursalID, Nombre, CodigoBarra, Categoria, "
                        "FechaCaducidad, Marca, Precio, Stock"
                    )

                branch_id = self.parse_int(row[0].strip(), "SucursalID")
                name = row[1].strip()
                barcode = row[2].strip()
                category = row[3].strip()
                expiry_date = row[4].strip()
                brand = row[5].strip()
                price = self.parse_float(row[6].strip(), "Precio")
                stock = self.parse_int(row[7].strip(), "Stock")

                if not name:
                    raise ValueError("Nombre de producto vacío")

                if not category:
                    raise ValueError("Categoría vacía")

                if not expiry_date:
                    raise ValueError("Fecha de caducidad vacía")

                if not self.is_valid_barcode(barcode):
                    raise ValueError("Código de barras inválido, debe tener 10 dígitos")

                if barcode in existing_barcodes:
                    raise ValueError(f"Código de barras duplicado: {barcode}")

                branch = branch_manager.find_by_id(branch_id)

                if branch is None:
                    raise ValueError(f"Sucursal no existe: {branch_id}")

                product = Product(name, barcode, category, expiry_date, brand, price, stock)
                inserted = branch.inventory.add_product(product)

                if inserted is False:
                    raise ValueError("No se pudo insertar el producto en todas las estructuras")

                existing_barcodes.add(barcode)
                loaded_count += 1

            except Exception as error:
                self.log_error(file_path, line_number, str(error))

        return loaded_count

    def load_all(self, branches_file, connections_file, products_file, branch_manager):
        self.clear_errors()

        branches_count = self.load_branches(branches_file, branch_manager)
        connections_count = self.load_connections(connections_file, branch_manager)
        products_count = self.load_products(products_file, branch_manager)

        return {
            "branches": branches_count,
            "connections": connections_count,
            "products": products_count,
            "error_log": self.error_log_path
        }