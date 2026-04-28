class TransferRequest:
    def __init__(self, source_id, destination_id, barcode, quantity, path, total_weight):
        self.source_id = source_id
        self.destination_id = destination_id
        self.barcode = barcode
        self.quantity = quantity
        self.path = path
        self.total_weight = total_weight
        self.status = "Pendiente"
        # simulation state
        self.current_index = 0
        self.remaining_time = 0
        self.completed = False

    def mark_completed(self):
        self.status = "Completada"

    def start(self):
        self.status = "En proceso"
        self.current_index = 0
        self.remaining_time = 0

    def set_step_time(self, time_cost):
        self.remaining_time = time_cost

    def tick(self):
        if self.completed:
            return

        if self.remaining_time > 0:
            self.remaining_time -= 1

        if self.remaining_time == 0:
            self.current_index += 1

            if self.current_index >= len(self.path):
                self.completed = True
                self.status = "Completada"
            else:
                self.status = f"En sucursal {self.path[self.current_index]}"

    def get_path_text(self):
        return " -> ".join(str(branch_id) for branch_id in self.path)