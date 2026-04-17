from app.models.product import Product


class Node:
    def __init__(self, data: Product):
        self.data = data
        self.next = None


class BaseLinkedList:
    def __init__(self):
        self.head = None

    def search_by_name(self, name: str):
        current = self.head

        while current is not None:
            if current.data.name == name:
                return current.data
            current = current.next

        return None

    def search_by_barcode(self, barcode: str):
        current = self.head

        while current is not None:
            if current.data.barcode == barcode:
                return current.data
            current = current.next

        return None

    def remove_by_barcode(self, barcode: str) -> bool:
        current = self.head
        previous = None

        while current is not None:
            if current.data.barcode == barcode:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                return True

            previous = current
            current = current.next

        return False

    def get_all_products(self):
        products = []
        current = self.head

        while current is not None:
            products.append(current.data)
            current = current.next

        return products