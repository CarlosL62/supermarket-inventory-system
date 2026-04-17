from app.services.catalog_service import CatalogService


class Branch:
    def __init__(self, id, name, location, entry_time, transfer_time, dispatch_interval):
        self.id = id
        self.name = name
        self.location = location
        self.entry_time = entry_time
        self.transfer_time = transfer_time
        self.dispatch_interval = dispatch_interval
        self.inventory = CatalogService()