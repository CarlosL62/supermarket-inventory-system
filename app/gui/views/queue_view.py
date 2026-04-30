from app.gui.helpers.table_loaders import load_transfer_queue_table


class QueueView:
    def __init__(self, branch_manager, transfers_table, result_label, parent=None):
        self.branch_manager = branch_manager
        self.transfers_table = transfers_table
        self.result_label = result_label
        self.parent = parent

    def refresh_queue_table(self):
        pending_transfers = self.branch_manager.get_pending_transfers()
        load_transfer_queue_table(self.transfers_table, pending_transfers, self.branch_manager)