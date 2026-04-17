from app.models.product import Product
from app.structures.unordered_linked_list import UnorderedLinkedList
from app.structures.ordered_linked_list import OrderedLinkedList
from app.structures.hash_table import HashTable
from app.structures.avl_tree import AVLTree
from app.structures.b_tree import BTree
from app.structures.b_plus_tree import BPlusTree


class CatalogService:
    def __init__(self):
        self.unordered_list = UnorderedLinkedList()
        self.ordered_list = OrderedLinkedList()
        self.hash_table = HashTable()
        self.avl_tree = AVLTree()
        self.b_tree = BTree()
        self.b_plus_tree = BPlusTree()

    def add_product(self, product: Product) -> bool:
        if self.hash_table.search(product.barcode) is not None:
            return False

        self.unordered_list.insert(product)
        self.ordered_list.insert(product)
        self.hash_table.insert(product)
        self.avl_tree.insert(product)
        self.b_tree.insert(product)
        self.b_plus_tree.insert(product)
        return True

    def delete_product_by_barcode(self, barcode: str) -> bool:
        product = self.hash_table.search(barcode)

        if product is None:
            return False

        self.unordered_list.remove_by_barcode(barcode)
        self.ordered_list.remove_by_barcode(barcode)
        self.hash_table.remove(barcode)
        self.avl_tree.remove(product.name)
        self.b_tree.remove(product.expiry_date)
        self.b_plus_tree.remove(product)
        return True

    def search_by_name(self, name: str):
        return self.avl_tree.search(name)

    def search_by_barcode(self, barcode: str):
        return self.hash_table.search(barcode)

    def search_by_category(self, category: str):
        return self.b_plus_tree.search(category)

    def search_by_expiry_date_range(self, start_date: str, end_date: str):
        return self.b_tree.search_by_range(start_date, end_date)

    def list_products_by_name(self):
        return self.avl_tree.in_order_traversal()

    def get_all_products(self):
        return self.unordered_list.get_all_products()
