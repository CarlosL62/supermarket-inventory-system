from app.models.branch import Branch
from app.models.product import Product


def load_demo_branches(branch_manager):
    branch_manager.add_branch(Branch(1, "Central", "Zona 1", 5, 3, 10))
    branch_manager.add_branch(Branch(2, "Norte", "Zona 5", 4, 2, 8))

    branches = branch_manager.get_branches()

    if len(branches) >= 1:
        branches[0].inventory.add_product(
            Product("Leche", "1234567890", "Lacteos", "2026-01-15", "LaVaquita", 12.50, 20)
        )
        branches[0].inventory.add_product(
            Product("Pan", "9876543210", "Panaderia", "2026-01-10", "Bimbo", 8.00, 35)
        )

    if len(branches) >= 2:
        branches[1].inventory.add_product(
            Product("Queso", "1112223334", "Lacteos", "2026-02-01", "Cremoso", 25.75, 10)
        )
