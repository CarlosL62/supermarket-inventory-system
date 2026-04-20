from PySide6.QtWidgets import QTableWidgetItem


def load_branches_table(table, branches):
    table.setRowCount(len(branches))

    for i, branch in enumerate(branches):
        table.setItem(i, 0, QTableWidgetItem(str(branch.id)))
        table.setItem(i, 1, QTableWidgetItem(branch.name))
        table.setItem(i, 2, QTableWidgetItem(branch.location))
        table.setItem(i, 3, QTableWidgetItem(str(branch.entry_time)))
        table.setItem(i, 4, QTableWidgetItem(str(branch.transfer_time)))
        table.setItem(i, 5, QTableWidgetItem(str(branch.dispatch_interval)))
        table.setItem(i, 6, QTableWidgetItem(str(len(branch.inventory.get_all_products()))))


def load_products_table(table, products):
    table.setRowCount(len(products))

    for i, product in enumerate(products):
        table.setItem(i, 0, QTableWidgetItem(product.name))
        table.setItem(i, 1, QTableWidgetItem(product.barcode))
        table.setItem(i, 2, QTableWidgetItem(product.category))
        table.setItem(i, 3, QTableWidgetItem(product.expiry_date))
        table.setItem(i, 4, QTableWidgetItem(product.brand))
        table.setItem(i, 5, QTableWidgetItem(str(product.price)))
        table.setItem(i, 6, QTableWidgetItem(str(product.stock)))


def load_connections_table(table, connections):
    table.setRowCount(len(connections))

    for i, (source_id, destination_id, weight) in enumerate(connections):
        table.setItem(i, 0, QTableWidgetItem(str(source_id)))
        table.setItem(i, 1, QTableWidgetItem(str(destination_id)))
        table.setItem(i, 2, QTableWidgetItem(str(weight)))