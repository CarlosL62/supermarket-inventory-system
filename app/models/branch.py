from app.services.catalog_service import CatalogService
from app.structures.transfer_queue import TransferQueue


class Branch:
    def __init__(self, id, name, location, entry_time, transfer_time, dispatch_interval):
        self.id = id
        self.name = name
        self.location = location
        self.entry_time = entry_time
        self.transfer_time = transfer_time
        self.dispatch_interval = dispatch_interval
        self.inventory = CatalogService()
        self.incoming_queue = TransferQueue()
        self.transfer_preparation_queue = TransferQueue()
        self.outgoing_queue = TransferQueue()

        # Runtime locks used by transfer worker threads to enforce FIFO behavior
        # Each branch can process only one transfer at a time per queue type
        self.incoming_queue_busy = False
        self.transfer_preparation_queue_busy = False
        self.outgoing_queue_busy = False