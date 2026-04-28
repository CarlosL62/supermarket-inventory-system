from PySide6.QtWidgets import QMessageBox
from app.gui.helpers.table_loaders import load_transfer_queue_table


class QueueView:
    def __init__(self, branch_manager, transfers_table, result_label, parent=None):
        self.branch_manager = branch_manager
        self.transfers_table = transfers_table
        self.result_label = result_label
        self.parent = parent

    def refresh_queue_table(self):
        pending_transfers = self.branch_manager.get_pending_transfers()
        load_transfer_queue_table(self.transfers_table, pending_transfers)

    def process_next_transfer(self):
        success, message, transfer_request = self.branch_manager.process_next_transfer()

        if not success:
            self.result_label.setText(f"Resultado: {message}")
            QMessageBox.warning(self.parent, "Cola de transferencias", message)
            return

        self.refresh_queue_table()
        result_text = f"Resultado: {message} | Ruta: {transfer_request.get_path_text()} | Peso total: {transfer_request.total_weight}"
        self.result_label.setText(result_text)
        QMessageBox.information(self.parent, "Cola de transferencias", result_text)