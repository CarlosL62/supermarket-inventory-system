import time
from threading import Lock
from PySide6.QtCore import QThread, Signal


class TransferWorker(QThread):
    updated = Signal(object)
    finished = Signal(object)

    # Shared FIFO control for all transfer workers.
    # Key: (branch_id, queue_name)
    # Value: ticket counters and busy state.
    queue_mutex = Lock()
    queue_next_ticket = {}
    queue_serving_ticket = {}
    queue_busy = {}

    def __init__(self, transfer_request, branch_manager, tick_seconds=1):
        super().__init__()
        self.transfer_request = transfer_request
        self.branch_manager = branch_manager
        self.tick_seconds = tick_seconds
        self.waiting_poll_seconds = min(tick_seconds, 0.1)
        self.is_running = True
        self.active_queue_lock = None
        self.queue_tickets = {}

    def get_current_step(self):
        steps = self.transfer_request.simulation_steps
        index = self.transfer_request.current_step_index

        if index < 0 or index >= len(steps):
            return None

        return steps[index]

    def get_queue_lock_name(self, step):
        if step is None:
            return None

        stage = step.get("stage", "")

        if stage == "Cola de ingreso":
            return "incoming_queue_busy"

        if stage == "Cola de preparación de traspaso":
            return "transfer_preparation_queue_busy"

        if stage == "Cola de salida":
            return "outgoing_queue_busy"

        return None

    def build_step_lock_key(self, step, queue_lock_name):
        if step is None or queue_lock_name is None:
            return None

        return (
            id(self.transfer_request),
            self.transfer_request.current_step_index,
            step.get("branch_id"),
            queue_lock_name
        )

    def build_queue_key(self, step, queue_lock_name):
        if step is None or queue_lock_name is None:
            return None

        return (
            step.get("branch_id"),
            queue_lock_name
        )

    def get_or_create_ticket(self, step, queue_lock_name):
        step_lock_key = self.build_step_lock_key(step, queue_lock_name)
        queue_key = self.build_queue_key(step, queue_lock_name)

        if step_lock_key in self.queue_tickets:
            return step_lock_key, queue_key, self.queue_tickets[step_lock_key]

        with TransferWorker.queue_mutex:
            next_ticket = TransferWorker.queue_next_ticket.get(queue_key, 0)
            TransferWorker.queue_next_ticket[queue_key] = next_ticket + 1
            TransferWorker.queue_serving_ticket.setdefault(queue_key, 0)
            TransferWorker.queue_busy.setdefault(queue_key, False)
            self.queue_tickets[step_lock_key] = next_ticket

        return step_lock_key, queue_key, next_ticket

    def reserve_current_queue_ticket(self):
        step = self.get_current_step()
        queue_lock_name = self.get_queue_lock_name(step)

        if queue_lock_name is None:
            return

        self.get_or_create_ticket(step, queue_lock_name)

    def set_waiting_fifo_status(self, step):
        waiting_text = f"Esperando FIFO - {step.get('stage', 'Cola')}"
        self.transfer_request.status = waiting_text
        self.transfer_request.current_stage = waiting_text
        self.updated.emit(self.transfer_request)

    def set_current_step_status(self, step):
        current_stage = step.get("stage", "En proceso")
        self.transfer_request.status = current_stage
        self.transfer_request.current_stage = current_stage
        self.updated.emit(self.transfer_request)

    def try_acquire_queue_lock(self):
        step = self.get_current_step()
        queue_lock_name = self.get_queue_lock_name(step)

        # Non-queue stages, such as transit, can advance independently.
        if queue_lock_name is None:
            return True

        branch_id = step.get("branch_id")
        branch = self.branch_manager.find_by_id(branch_id)

        if branch is None:
            return True

        step_lock_key, queue_key, ticket = self.get_or_create_ticket(step, queue_lock_name)

        with TransferWorker.queue_mutex:
            if self.active_queue_lock == (branch, queue_lock_name, step_lock_key, queue_key, ticket):
                return True

            serving_ticket = TransferWorker.queue_serving_ticket.get(queue_key, 0)
            is_busy = TransferWorker.queue_busy.get(queue_key, False)

            if ticket == serving_ticket and not is_busy:
                TransferWorker.queue_busy[queue_key] = True
                setattr(branch, queue_lock_name, True)
                self.active_queue_lock = (branch, queue_lock_name, step_lock_key, queue_key, ticket)
                can_process = True
            else:
                can_process = False

        if not can_process:
            self.set_waiting_fifo_status(step)
            return False

        self.set_current_step_status(step)
        return True

    def release_queue_lock(self):
        if self.active_queue_lock is None:
            return

        branch, queue_lock_name, _, queue_key, ticket = self.active_queue_lock

        with TransferWorker.queue_mutex:
            TransferWorker.queue_busy[queue_key] = False
            current_serving_ticket = TransferWorker.queue_serving_ticket.get(queue_key, ticket)

            if current_serving_ticket <= ticket:
                TransferWorker.queue_serving_ticket[queue_key] = ticket + 1

        setattr(branch, queue_lock_name, False)
        self.active_queue_lock = None

    def run(self):
        try:
            while self.is_running and not self.transfer_request.completed:
                previous_step_index = self.transfer_request.current_step_index

                if not self.try_acquire_queue_lock():
                    # Waiting in FIFO does not consume processing time.
                    time.sleep(self.waiting_poll_seconds)
                    continue

                self.transfer_request.tick()
                self.updated.emit(self.transfer_request)

                current_step_index = self.transfer_request.current_step_index

                if current_step_index != previous_step_index or self.transfer_request.completed:
                    self.release_queue_lock()

                time.sleep(self.tick_seconds)
        finally:
            self.release_queue_lock()
            self.finished.emit(self.transfer_request)

    def stop(self):
        self.is_running = False
