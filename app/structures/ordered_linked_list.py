from app.structures.base_linked_list import BaseLinkedList, Node
from app.models.product import Product


class OrderedLinkedList(BaseLinkedList):
    def insert(self, product: Product):
        new_node = Node(product)

        if self.head is None or product.name.lower() < self.head.data.name.lower():
            new_node.next = self.head
            self.head = new_node
            return

        current = self.head

        while current.next is not None and current.next.data.name.lower() < product.name.lower():
            current = current.next

        new_node.next = current.next
        current.next = new_node