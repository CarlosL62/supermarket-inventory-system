from app.models.product import Product


class BPlusTreeNode:
    # Node structure for B+ Tree
    # keys: separator keys (categories)
    # values: only used in leaf nodes (list of product lists)
    # children: pointers to child nodes (for internal nodes)
    # next: pointer to next leaf node (for sequential access)
    def __init__(self, is_leaf: bool):
        self.keys = []
        self.values = []
        self.children = []
        self.is_leaf = is_leaf
        self.next = None


class BPlusTree:
    def __init__(self, min_degree=3):
        self.root = None
        self.min_degree = min_degree

    def find_leaf(self, category: str):
        if self.root is None:
            return None

        # Traverse down the tree until reaching a leaf node
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

        # Look for the category inside the leaf node
        for i in range(len(leaf.keys)):
            if leaf.keys[i] == category:
                return leaf.values[i]

        return []

    def insert(self, product: Product):
        # If tree is empty, create the first leaf node
        if self.root is None:
            self.root = BPlusTreeNode(True)
            self.root.keys.append(product.category)
            self.root.values.append([product])
            return

        # If root is full, split it before inserting
        if len(self.root.keys) == 2 * self.min_degree - 1:
            new_root = BPlusTreeNode(False)
            new_root.children.append(self.root)
            self.split_child(new_root, 0)
            self.root = new_root

        self.insert_non_full(self.root, product)

    def insert_non_full(self, node, product: Product):
        i = len(node.keys) - 1

        # Insert directly if node is a leaf
        if node.is_leaf:
            while i >= 0 and product.category < node.keys[i]:
                i -= 1

            if i >= 0 and node.keys[i] == product.category:
                node.values[i].append(product)
                return

            node.keys.insert(i + 1, product.category)
            node.values.insert(i + 1, [product])
            return

        # Otherwise, traverse to the correct child
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

        # Splitting a leaf node: keep data in leaves and update links
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
            # Splitting an internal node: promote middle key
            promoted_key = full_child.keys[middle_index]

            new_child.keys = full_child.keys[middle_index + 1:]
            new_child.children = full_child.children[middle_index + 1:]

            full_child.keys = full_child.keys[:middle_index]
            full_child.children = full_child.children[:middle_index + 1]

            parent.keys.insert(child_index, promoted_key)
            parent.children.insert(child_index + 1, new_child)

    def remove(self, product: Product):
        # Safe deletion: rebuild tree after removing the target product
        if self.root is None:
            return

        remaining_products = []
        removed = False

        for current_product in self.get_all_products():
            same_category = current_product.category == product.category
            same_barcode = current_product.barcode == product.barcode

            if same_category and same_barcode and not removed:
                removed = True
                continue

            remaining_products.append(current_product)

        if not removed:
            return

        self._rebuild_from_products(remaining_products)


    def _rebuild_from_products(self, products):
        # Rebuild the tree from remaining products to maintain B+ properties
        self.root = None

        for product in products:
            self.insert(product)

    def get_all_products(self):
        products = []
        current = self.root

        if current is None:
            return products

        # Move to the leftmost leaf
        while not current.is_leaf:
            current = current.children[0]

        # Traverse leaf nodes using 'next' pointers
        while current is not None:
            for category_products in current.values:
                products.extend(category_products)
            current = current.next

        return products
