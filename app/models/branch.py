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