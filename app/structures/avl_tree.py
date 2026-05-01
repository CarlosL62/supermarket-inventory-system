from app.models.product import Product


class AVLNode:
    def __init__(self, product: Product):
        self.product = product
        self.left = None
        self.right = None
        self.height = 1


class AVLTree:
    def __init__(self):
        self.root = None

    def _get_height(self, node):
        if node is None:
            return 0
        return node.height

    def _get_balance(self, node):
        if node is None:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _right_rotate(self, y):
        x = y.left
        t2 = x.right

        # Move y down to the right side of x
        x.right = y
        y.left = t2

        # Heights must be updated from bottom to top after rotating
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))

        return x

    def _left_rotate(self, x):
        y = x.right
        t2 = y.left

        # Move x down to the left side of y
        y.left = x
        x.right = t2

        # Heights must be updated from bottom to top after rotating
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def insert(self, product: Product):
        self.root = self._insert(self.root, product)

    def _insert(self, node, product: Product):
        if node is None:
            return AVLNode(product)

        if product.name.lower() < node.product.name.lower():
            node.left = self._insert(node.left, product)
        elif product.name.lower() > node.product.name.lower():
            node.right = self._insert(node.right, product)
        else:
            return node

        # Update height before checking the balance factor
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        # Rebalance the four AVL insertion cases
        if balance > 1 and product.name.lower() < node.left.product.name.lower():
            return self._right_rotate(node)

        if balance < -1 and product.name.lower() > node.right.product.name.lower():
            return self._left_rotate(node)

        if balance > 1 and product.name.lower() > node.left.product.name.lower():
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        if balance < -1 and product.name.lower() < node.right.product.name.lower():
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def search(self, name: str):
        return self._search(self.root, name)

    def remove(self, name: str):
        self.root = self._remove(self.root, name)

    def _remove(self, node, name: str):
        if node is None:
            return None

        if name.lower() < node.product.name.lower():
            node.left = self._remove(node.left, name)
        elif name.lower() > node.product.name.lower():
            node.right = self._remove(node.right, name)
        else:
            # Node with one child or no child
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # Node with two children: replace it with the inorder successor
            successor = self._get_min_value_node(node.right)
            node.product = successor.product
            node.right = self._remove(node.right, successor.product.name)

        if node is None:
            return None

        # Update height before checking the balance factor after deletion
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        # Rebalance the four AVL deletion cases
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)

        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)

        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def _get_min_value_node(self, node):
        current = node

        while current.left is not None:
            current = current.left

        return current

    def _search(self, node, name: str):
        if node is None:
            return None

        if name.lower() == node.product.name.lower():
            return node.product

        if name.lower() < node.product.name.lower():
            return self._search(node.left, name)

        return self._search(node.right, name)

    def in_order_traversal(self):
        products = []
        self._in_order_traversal(self.root, products)
        return products

    def _in_order_traversal(self, node, products):
        if node is not None:
            self._in_order_traversal(node.left, products)
            products.append(node.product)
            self._in_order_traversal(node.right, products)

    def get_all_products(self):
        return self.in_order_traversal()