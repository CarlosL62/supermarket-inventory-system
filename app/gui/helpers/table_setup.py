from PySide6.QtWidgets import QHeaderView, QAbstractItemView


def setup_branches_table(table):
    table.setColumnCount(7)
    table.setHorizontalHeaderLabels([
        "ID", "Nombre", "Ubicación",
        "Tiempo ingreso", "Tiempo traspaso", "Intervalo despacho",
        "Cantidad productos"
    ])
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)


def setup_products_table(table):
    table.setColumnCount(7)
    table.setHorizontalHeaderLabels([
        "Nombre", "Código", "Categoría",
        "Fecha", "Marca", "Precio", "Stock"
    ])
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)


def setup_connections_table(table):
    table.setColumnCount(3)
    table.setHorizontalHeaderLabels([
        "Origen", "Destino", "Peso"
    ])
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)