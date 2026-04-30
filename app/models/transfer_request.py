class TransferRequest:
    def __init__(self, source_id, destination_id, barcode, quantity, path, total_weight):
        self.source_id = source_id
        self.destination_id = destination_id
        self.barcode = barcode
        self.quantity = quantity
        self.path = path
        self.total_weight = total_weight
        self.status = "Pendiente"
        self.current_stage = "Pendiente"

        # Simulation state
        self.current_index = 0
        self.remaining_time = 0
        self.total_eta = 0
        self.estimated_total_time = 0
        self.elapsed_time = 0
        self.completed = False

    def mark_completed(self):
        self.completed = True
        self.status = "Completada"
        self.current_stage = "Completada"
        self.remaining_time = 0

    def start(self):
        self.status = "En proceso"
        self.current_stage = "En cola de salida"
        self.current_index = 0
        self.remaining_time = 0
        self.elapsed_time = 0

    def set_step_time(self, time_cost, stage_name=None):
        self.remaining_time = time_cost
        if self.estimated_total_time == 0:
            self.total_eta += time_cost

        if stage_name is not None:
            self.current_stage = stage_name
            self.status = stage_name

    def set_estimated_total_time(self, estimated_total_time):
        self.estimated_total_time = estimated_total_time
        self.total_eta = estimated_total_time

    def tick(self):
        if self.completed:
            return

        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.elapsed_time += 1

        if self.remaining_time == 0:
            self.current_index += 1

            if self.current_index >= len(self.path):
                self.mark_completed()
            else:
                self.current_stage = f"En sucursal {self.path[self.current_index]}"
                self.status = self.current_stage

    def get_current_branch_id(self):
        if not self.path:
            return None

        if self.current_index >= len(self.path):
            return self.path[-1]

        return self.path[self.current_index]

    def get_eta_remaining(self):
        return max(self.total_eta - self.elapsed_time, 0)

    def get_progress_text(self):
        if self.completed:
            return "100%"

        if self.total_eta == 0:
            return "0%"

        progress = min((self.elapsed_time / self.total_eta) * 100, 99)
        return f"{progress:.0f}%"

    def get_path_text(self):
        return " -> ".join(str(branch_id) for branch_id in self.path)