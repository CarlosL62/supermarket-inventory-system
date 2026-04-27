from app.models.branch import Branch
from app.models.branch_graph import BranchGraph
from copy import copy


class BranchManager:
    def __init__(self):
        self.branches = []
        self.next_branch_id = 1
        self.graph = BranchGraph()

    def add_branch(self, branch: Branch):
        # Branch ids are assigned here to avoid duplicates after deletions
        if branch.id is None or branch.id <= 0:
            branch.id = self.next_branch_id
            self.next_branch_id += 1
        elif branch.id >= self.next_branch_id:
            self.next_branch_id = branch.id + 1

        self.branches.append(branch)
        self.graph.add_branch(branch.id)
        return branch

    def get_branches(self):
        return self.branches

    def find_by_id(self, branch_id):
        for branch in self.branches:
            if branch.id == branch_id:
                return branch
        return None

    def delete_branch(self, branch_id):
        branch = self.find_by_id(branch_id)
        if branch is None:
            return False

        self.branches.remove(branch)
        self.graph.remove_branch(branch_id)
        return True

    def connect_branches(self, source_id, destination_id, weight):
        source_branch = self.find_by_id(source_id)
        destination_branch = self.find_by_id(destination_id)

        if source_branch is None or destination_branch is None:
            return False

        if source_id == destination_id:
            return False

        return self.graph.add_connection(source_id, destination_id, weight)

    def find_product_in_branch(self, branch, barcode):
        for product in branch.inventory.get_all_products():
            if product.barcode == barcode:
                return product
        return None

    def transfer_product(self, source_id, destination_id, barcode, quantity):
        source_branch = self.find_by_id(source_id)
        destination_branch = self.find_by_id(destination_id)

        if source_branch is None is None:
            return False, "Sucursal origen no encontrada", [], None

        if destination_branch is None:
            return False, "Sucursal destino no encontrada", [], None

        if source_id == destination_id:
            return False, "La sucursal origen y destino no pueden ser iguales", [], None

        if quantity <= 0:
            return False, "La cantidad debe ser mayor que cero", [], None

        path, total_weight = self.graph.shortest_path(source_id, destination_id)
        if not path:
            return False, "No existe una ruta entre las sucursales", [], None

        source_product = self.find_product_in_branch(source_branch, barcode)
        if source_product is None:
            return False, "El producto no existe en la sucursal origen", [], None

        if source_product.stock < quantity:
            return False, "Stock insuficiente en la sucursal origen", [], None

        destination_product = self.find_product_in_branch(destination_branch, barcode)

        source_product.stock -= quantity

        if destination_product is not None:
            destination_product.stock += quantity
        else:
            transferred_product = copy(source_product)
            transferred_product.stock = quantity
            destination_branch.inventory.add_product(transferred_product)

        return True, "Transferencia realizada correctamente", path, total_weight