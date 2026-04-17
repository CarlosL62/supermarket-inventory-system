from app.structures.base_linked_list import BaseLinkedList, Node
from app.models.product import Product


class UnorderedLinkedList(BaseLinkedList):
    def insert(self, product: Product):
        new_node = Node(product)
        new_node.next = self.head
        self.head = new_node