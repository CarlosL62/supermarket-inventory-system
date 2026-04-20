from app.models.product import Product


class HashTable:
    def __init__(self, capacity=1501):
        self.capacity = capacity
        self.table = [[] for _ in range(capacity)]

    def _hash_function(self, barcode: str) -> int:
        return sum(ord(char) for char in barcode) % self.capacity

    def insert(self, product: Product) -> bool:
        index = self._hash_function(product.barcode)
        bucket = self.table[index]

        for existing_product in bucket:
            if existing_product.barcode == product.barcode:
                return False

        bucket.append(product)
        return True

    def search(self, barcode: str):
        index = self._hash_function(barcode)
        bucket = self.table[index]

        for product in bucket:
            if product.barcode == barcode:
                return product

        return None

    def remove(self, barcode: str) -> bool:
        index = self._hash_function(barcode)
        bucket = self.table[index]

        for i, product in enumerate(bucket):
            if product.barcode == barcode:
                del bucket[i]
                return True

        return False

    def get_all_products(self):
        products = []

        for bucket in self.table:
            products.extend(bucket)

        return products