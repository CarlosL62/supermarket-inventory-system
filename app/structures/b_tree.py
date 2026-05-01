from app.models.product import Product


class BTreeNode:
    def __init__(self, is_leaf: bool):
        self.keys = []
        self.children = []
        self.is_leaf = is_leaf


class BTree:
    def __init__(self, min_degree=3):
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
        if self.root is None:
            return

        self._remove(self.root, expiry_date)

        if len(self.root.keys) == 0:
            if self.root.is_leaf:
                self.root = None
            else:
                self.root = self.root.children[0]

    def _remove(self, node, expiry_date: str):
        index = self._find_key_index(node, expiry_date)

        if index < len(node.keys) and node.keys[index].expiry_date == expiry_date:
            if node.is_leaf:
                self._remove_from_leaf(node, index)
            else:
                self._remove_from_internal(node, index)
            return

        if node.is_leaf:
            return

        child_index = index
        child = node.children[child_index]

        if len(child.keys) < self.min_degree:
            self._fill_child(node, child_index)

            if child_index > len(node.keys):
                child_index -= 1

        self._remove(node.children[child_index], expiry_date)


    def _find_key_index(self, node, expiry_date: str):
        index = 0

        while index < len(node.keys) and node.keys[index].expiry_date < expiry_date:
            index += 1

        return index

    def _remove_from_leaf(self, node, index: int):
        del node.keys[index]

    def _remove_from_internal(self, node, index: int):
        key = node.keys[index]
        left_child = node.children[index]
        right_child = node.children[index + 1]

        if len(left_child.keys) >= self.min_degree:
            predecessor = self._get_predecessor(left_child)
            node.keys[index] = predecessor
            self._remove(left_child, predecessor.expiry_date)
        elif len(right_child.keys) >= self.min_degree:
            successor = self._get_successor(right_child)
            node.keys[index] = successor
            self._remove(right_child, successor.expiry_date)
        else:
            self._merge_children(node, index)
            self._remove(left_child, key.expiry_date)

    def _get_predecessor(self, node):
        current = node

        while not current.is_leaf:
            current = current.children[-1]

        return current.keys[-1]

    def _get_successor(self, node):
        current = node

        while not current.is_leaf:
            current = current.children[0]

        return current.keys[0]

    def _fill_child(self, parent, child_index: int):
        if child_index > 0 and len(parent.children[child_index - 1].keys) >= self.min_degree:
            self._borrow_from_previous(parent, child_index)
        elif child_index < len(parent.children) - 1 and len(parent.children[child_index + 1].keys) >= self.min_degree:
            self._borrow_from_next(parent, child_index)
        else:
            if child_index < len(parent.children) - 1:
                self._merge_children(parent, child_index)
            else:
                self._merge_children(parent, child_index - 1)

    def _borrow_from_previous(self, parent, child_index: int):
        child = parent.children[child_index]
        sibling = parent.children[child_index - 1]

        child.keys.insert(0, parent.keys[child_index - 1])

        if not child.is_leaf:
            child.children.insert(0, sibling.children.pop())

        parent.keys[child_index - 1] = sibling.keys.pop()

    def _borrow_from_next(self, parent, child_index: int):
        child = parent.children[child_index]
        sibling = parent.children[child_index + 1]

        child.keys.append(parent.keys[child_index])

        if not child.is_leaf:
            child.children.append(sibling.children.pop(0))

        parent.keys[child_index] = sibling.keys.pop(0)

    def _merge_children(self, parent, child_index: int):
        child = parent.children[child_index]
        sibling = parent.children[child_index + 1]

        child.keys.append(parent.keys.pop(child_index))
        child.keys.extend(sibling.keys)

        if not child.is_leaf:
            child.children.extend(sibling.children)

        parent.children.pop(child_index + 1)

    def get_all_products(self):
        return self.search_by_range("0000-01-01", "9999-12-31")