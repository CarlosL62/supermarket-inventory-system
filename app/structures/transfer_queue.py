class TransferQueue:
    def __init__(self):
        self.items = []

    def enqueue(self, transfer_request):
        self.items.append(transfer_request)

    def dequeue(self):
        if self.is_empty():
            return None

        return self.items.pop(0)

    def peek(self):
        if self.is_empty():
            return None

        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def get_all(self):
        return self.items