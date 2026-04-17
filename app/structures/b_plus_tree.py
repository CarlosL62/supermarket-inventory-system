from app.models.product import Product


class BPlusTreeNode:
    def __init__(self, is_leaf: bool):
        self.keys = []
        self.values = []
        self.children = []
        self.is_leaf = is_leaf
        self.next = None


class BPlusTree:
    def __init__(self, min_degree=2):
        self.root = None
        self.min_degree = min_degree

    def find_leaf(self, category: str):
        if self.root is None:
            return None

        current = self.root

        while not current.is_leaf:
            i = 0
            while i < len(current.keys) and category >= current.keys[i]:
                i += 1
            current = current.children[i]

        return current

    def search(self, category: str):
        leaf = self.find_leaf(category)

        if leaf is None:
            return []

        for i in range(len(leaf.keys)):
            if leaf.keys[i] == category:
                return leaf.values[i]

        return []

    def insert(self, product: Product):
        if self.root is None:
            self.root = BPlusTreeNode(True)
            self.root.keys.append(product.category)
            self.root.values.append([product])
            return

        if len(self.root.keys) == 2 * self.min_degree - 1:
            new_root = BPlusTreeNode(False)
            new_root.children.append(self.root)
            self.split_child(new_root, 0)
            self.root = new_root

        self.insert_non_full(self.root, product)

    def insert_non_full(self, node, product: Product):
        i = len(node.keys) - 1

        if node.is_leaf:
            while i >= 0 and product.category < node.keys[i]:
                i -= 1

            if i >= 0 and node.keys[i] == product.category:
                node.values[i].append(product)
                return

            node.keys.insert(i + 1, product.category)
            node.values.insert(i + 1, [product])
            return

        while i >= 0 and product.category < node.keys[i]:
            i -= 1

        i += 1

        if len(node.children[i].keys) == 2 * self.min_degree - 1:
            self.split_child(node, i)

            if product.category >= node.keys[i]:
                i += 1

        self.insert_non_full(node.children[i], product)

    def split_child(self, parent, child_index: int):
        full_child = parent.children[child_index]
        new_child = BPlusTreeNode(full_child.is_leaf)
        middle_index = self.min_degree - 1

        if full_child.is_leaf:
            new_child.keys = full_child.keys[middle_index:]
            new_child.values = full_child.values[middle_index:]

            full_child.keys = full_child.keys[:middle_index]
            full_child.values = full_child.values[:middle_index]

            new_child.next = full_child.next
            full_child.next = new_child

            parent.keys.insert(child_index, new_child.keys[0])
            parent.children.insert(child_index + 1, new_child)
        else:
            promoted_key = full_child.keys[middle_index]

            new_child.keys = full_child.keys[middle_index + 1:]
            new_child.children = full_child.children[middle_index + 1:]

            full_child.keys = full_child.keys[:middle_index]
            full_child.children = full_child.children[:middle_index + 1]

            parent.keys.insert(child_index, promoted_key)
            parent.children.insert(child_index + 1, new_child)

    def remove(self, product: Product):
        self._remove(self.root, product)

        if self.root is not None and not self.root.is_leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0] if self.root.children else None

        if self.root is not None and self.root.is_leaf and len(self.root.keys) == 0:
            self.root = None

    def _remove(self, node, product: Product):
        if node is None:
            return

        if not node.is_leaf:
            i = 0
            while i < len(node.keys) and product.category >= node.keys[i]:
                i += 1
            self._remove(node.children[i], product)
            return

        for i in range(len(node.keys)):
            if node.keys[i] == product.category:
                category_products = node.values[i]

                for j in range(len(category_products)):
                    if category_products[j].barcode == product.barcode:
                        del category_products[j]
                        break

                if len(category_products) == 0:
                    del node.keys[i]
                    del node.values[i]

                return

    def get_all_products(self):
        products = []
        current = self.root

        if current is None:
            return products

        while not current.is_leaf:
            current = current.children[0]

        while current is not None:
            for category_products in current.values:
                products.extend(category_products)
            current = current.next

        return products
