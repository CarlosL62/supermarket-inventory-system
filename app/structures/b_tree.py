from app.models.product import Product


class BTreeNode:
    def __init__(self, is_leaf: bool):
        self.keys = []
        self.children = []
        self.is_leaf = is_leaf


class BTree:
    def __init__(self, min_degree=2):
        self.root = None
        self.min_degree = min_degree

    def search(self, expiry_date: str):
        return self._search(self.root, expiry_date)

    def _search(self, node, expiry_date: str):
        if node is None:
            return None

        i = 0
        while i < len(node.keys) and expiry_date > node.keys[i].expiry_date:
            i += 1

        if i < len(node.keys) and node.keys[i].expiry_date == expiry_date:
            return node.keys[i]

        if node.is_leaf:
            return None

        return self._search(node.children[i], expiry_date)

    def insert(self, product: Product):
        if self.root is None:
            self.root = BTreeNode(True)
            self.root.keys.append(product)
            return

        if len(self.root.keys) == 2 * self.min_degree - 1:
            new_root = BTreeNode(False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root

        self._insert_non_full(self.root, product)

    def _insert_non_full(self, node, product: Product):
        i = len(node.keys) - 1

        if node.is_leaf:
            node.keys.append(product)

            while i >= 0 and product.expiry_date < node.keys[i].expiry_date:
                node.keys[i + 1] = node.keys[i]
                i -= 1

            node.keys[i + 1] = product
            return

        while i >= 0 and product.expiry_date < node.keys[i].expiry_date:
            i -= 1

        i += 1

        if len(node.children[i].keys) == 2 * self.min_degree - 1:
            self._split_child(node, i)

            if product.expiry_date > node.keys[i].expiry_date:
                i += 1

        self._insert_non_full(node.children[i], product)

    def _split_child(self, parent, child_index: int):
        full_child = parent.children[child_index]
        new_child = BTreeNode(full_child.is_leaf)
        middle_index = self.min_degree - 1

        promoted_key = full_child.keys[middle_index]

        new_child.keys = full_child.keys[middle_index + 1:]
        full_child.keys = full_child.keys[:middle_index]

        if not full_child.is_leaf:
            new_child.children = full_child.children[middle_index + 1:]
            full_child.children = full_child.children[:middle_index + 1]

        parent.keys.insert(child_index, promoted_key)
        parent.children.insert(child_index + 1, new_child)

    def search_by_range(self, start_date: str, end_date: str):
        results = []
        self._search_by_range(self.root, start_date, end_date, results)
        return results

    def _search_by_range(self, node, start_date: str, end_date: str, results):
        if node is None:
            return

        i = 0

        while i < len(node.keys):
            if not node.is_leaf:
                self._search_by_range(node.children[i], start_date, end_date, results)

            if start_date <= node.keys[i].expiry_date <= end_date:
                results.append(node.keys[i])

            i += 1

        if not node.is_leaf:
            self._search_by_range(node.children[i], start_date, end_date, results)

    def remove(self, expiry_date: str):
        self._remove(self.root, expiry_date)

        if self.root is not None and not self.root.is_leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0] if self.root.children else None

        if self.root is not None and self.root.is_leaf and len(self.root.keys) == 0:
            self.root = None

    def _remove(self, node, expiry_date: str):
        if node is None:
            return

        i = 0
        while i < len(node.keys) and expiry_date > node.keys[i].expiry_date:
            i += 1

        if i < len(node.keys) and node.keys[i].expiry_date == expiry_date:
            if node.is_leaf:
                del node.keys[i]
                return

            successor = self._get_successor(node, i)
            node.keys[i] = successor
            self._remove(node.children[i + 1], successor.expiry_date)
            return

        if node.is_leaf:
            return

        if i < len(node.children):
            self._remove(node.children[i], expiry_date)

    def _get_successor(self, node, index: int):
        current = node.children[index + 1]

        while not current.is_leaf:
            current = current.children[0]

        return current.keys[0]

    def get_all_products(self):
        return self.search_by_range("0000-01-01", "9999-12-31")