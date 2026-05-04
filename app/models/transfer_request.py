class TransferRequest:
    def __init__(self, source_id, destination_id, barcode, quantity, path, total_weight, criterion="time"):
        self.source_id = source_id
        self.destination_id = destination_id
        self.barcode = barcode
        self.quantity = quantity
        self.path = path
        self.total_weight = total_weight
        self.criterion = criterion
        self.status = "Pendiente"
        self.current_stage = "Pendiente"

        # Simulation state
        self.current_index = 0
        self.remaining_time = 0
        self.total_eta = 0
        self.estimated_total_time = 0
        self.elapsed_time = 0
        self.completed = False
        self.applied = False

        # Detailed simulation steps. Each step is a dictionary with:
        # branch_id, stage, duration, and optional description
        self.simulation_steps = []
        self.current_step_index = 0

    def mark_completed(self):
        self.completed = True
        self.status = "Completada"
        self.current_stage = "Completada"
        self.remaining_time = 0

    def start(self):
        self.status = "En proceso"
        self.current_index = 0
        self.current_step_index = 0
        self.remaining_time = 0
        self.elapsed_time = 0
        self.completed = False

        if self.simulation_steps:
            self.activate_current_step()
        else:
            self.current_stage = "En cola de salida"

    def configure_simulation_steps(self, simulation_steps):
        self.simulation_steps = simulation_steps or []
        self.current_step_index = 0

        if self.estimated_total_time == 0:
            self.set_estimated_total_time(
                sum(step.get("duration", 0) for step in self.simulation_steps)
            )

    def activate_current_step(self):
        if self.current_step_index >= len(self.simulation_steps):
            self.mark_completed()
            return

        current_step = self.simulation_steps[self.current_step_index]
        self.current_stage = current_step.get("stage", "En proceso")
        self.status = self.current_stage
        self.remaining_time = current_step.get("duration", 0)

        branch_id = current_step.get("branch_id")
        if branch_id in self.path:
            self.current_index = self.path.index(branch_id)

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

        if self.simulation_steps:
            if self.remaining_time > 0:
                self.remaining_time -= 1
                self.elapsed_time += 1

            if self.remaining_time == 0:
                self.current_step_index += 1
                self.activate_current_step()

            return

        # Fallback behavior for transfers without configured simulation steps.
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
        if self.simulation_steps and self.current_step_index < len(self.simulation_steps):
            branch_id = self.simulation_steps[self.current_step_index].get("branch_id")
            if branch_id is not None:
                return branch_id

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