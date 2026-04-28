from app.models.branch import Branch
from app.models.product import Product


def load_demo_branches(branch_manager):
    branch_manager.add_branch(Branch(1, "Central", "Zona 1", 5, 3, 10))
    branch_manager.add_branch(Branch(2, "Norte", "Zona 5", 4, 2, 8))
    branch_manager.add_branch(Branch(3, "Sur", "Zona 12", 6, 4, 12))
    branch_manager.add_branch(Branch(4, "Occidente", "Zona 7", 7, 5, 15))
    branch_manager.add_branch(Branch(5, "Sin conexión", "Zona 18", 3, 2, 6))

    branch_manager.connect_branches(1, 2, 10, 3, True)
    branch_manager.connect_branches(1, 3, 4, 9, True)
    branch_manager.connect_branches(3, 2, 3, 8, True)
    branch_manager.connect_branches(2, 4, 8, 2, True)
    branch_manager.connect_branches(3, 4, 2, 10, True)

    branches = branch_manager.get_branches()

    if len(branches) >= 1:
        branches[0].inventory.add_product(
            Product("Leche", "1234567890", "Lacteos", "2026-01-15", "LaVaquita", 12.50, 20)
        )
        branches[0].inventory.add_product(
            Product("Pan", "9876543210", "Panaderia", "2026-01-10", "Bimbo", 8.00, 35)
        )
        branches[0].inventory.add_product(
            Product("Banana", "1000000001", "Frutas", "2026-02-20", "Tropical", 3.25, 50)
        )

    if len(branches) >= 2:
        branches[1].inventory.add_product(
            Product("Queso", "1112223334", "Lacteos", "2026-02-01", "Cremoso", 25.75, 10)
        )
        branches[1].inventory.add_product(
            Product("Manzana", "1000000002", "Frutas", "2026-03-10", "DelCampo", 4.50, 40)
        )

    if len(branches) >= 3:
        branches[2].inventory.add_product(
            Product("Arroz", "1000000003", "Granos", "2026-04-05", "DonMaiz", 9.75, 80)
        )
        branches[2].inventory.add_product(
            Product("Jugo", "1000000004", "Bebidas", "2026-01-30", "Natural", 7.25, 25)
        )

    if len(branches) >= 4:
        branches[3].inventory.add_product(
            Product("Frijol", "1000000005", "Granos", "2026-05-12", "Chapines", 11.00, 60)
        )
        branches[3].inventory.add_product(
            Product("Yogurt", "1000000006", "Lacteos", "2026-02-18", "Cremoso", 6.75, 18)
        )

    if len(branches) >= 5:
        branches[4].inventory.add_product(
            Product("Cereal", "1000000007", "Desayuno", "2026-06-01", "Crunchy", 18.50, 22)
        )
