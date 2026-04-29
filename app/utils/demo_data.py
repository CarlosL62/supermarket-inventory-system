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
        branches[0].inventory.add_product(
            Product("Aceite", "1000000008", "Despensa", "2026-07-15", "OlivaMax", 22.75, 16)
        )
        branches[0].inventory.add_product(
            Product("Cafe", "1000000009", "Bebidas", "2026-08-05", "BuenDia", 31.50, 14)
        )
        branches[0].inventory.add_product(
            Product("Galletas", "1000000010", "Snacks", "2026-03-22", "DulceHogar", 9.25, 45)
        )
        branches[0].inventory.add_product(
            Product("Huevos", "1000000011", "Proteinas", "2026-01-25", "Granjita", 28.00, 30)
        )

    if len(branches) >= 2:
        branches[1].inventory.add_product(
            Product("Queso", "1112223334", "Lacteos", "2026-02-01", "Cremoso", 25.75, 10)
        )
        branches[1].inventory.add_product(
            Product("Manzana", "1000000002", "Frutas", "2026-03-10", "DelCampo", 4.50, 40)
        )
        branches[1].inventory.add_product(
            Product("Pasta", "1000000012", "Despensa", "2026-09-12", "LaItaliana", 6.80, 55)
        )
        branches[1].inventory.add_product(
            Product("Atun", "1000000013", "Enlatados", "2027-01-20", "MarAzul", 12.40, 32)
        )
        branches[1].inventory.add_product(
            Product("Papel Higienico", "1000000014", "Higiene", "2027-03-01", "Suave", 24.90, 20)
        )
        branches[1].inventory.add_product(
            Product("Tomate", "1000000015", "Verduras", "2026-02-14", "Fresco", 5.10, 38)
        )

    if len(branches) >= 3:
        branches[2].inventory.add_product(
            Product("Arroz", "1000000003", "Granos", "2026-04-05", "DonMaiz", 9.75, 80)
        )
        branches[2].inventory.add_product(
            Product("Jugo", "1000000004", "Bebidas", "2026-01-30", "Natural", 7.25, 25)
        )
        branches[2].inventory.add_product(
            Product("Sal", "1000000016", "Despensa", "2027-04-18", "Marina", 3.40, 70)
        )
        branches[2].inventory.add_product(
            Product("Azucar", "1000000017", "Despensa", "2026-11-09", "Dulzura", 8.60, 64)
        )
        branches[2].inventory.add_product(
            Product("Detergente", "1000000018", "Limpieza", "2027-05-03", "Brillante", 19.75, 28)
        )
        branches[2].inventory.add_product(
            Product("Cebolla", "1000000019", "Verduras", "2026-02-28", "Fresco", 4.20, 42)
        )

    if len(branches) >= 4:
        branches[3].inventory.add_product(
            Product("Frijol", "1000000005", "Granos", "2026-05-12", "Chapines", 11.00, 60)
        )
        branches[3].inventory.add_product(
            Product("Yogurt", "1000000006", "Lacteos", "2026-02-18", "Cremoso", 6.75, 18)
        )
        branches[3].inventory.add_product(
            Product("Avena", "1000000020", "Desayuno", "2026-10-30", "NaturalFit", 13.30, 26)
        )
        branches[3].inventory.add_product(
            Product("Miel", "1000000021", "Despensa", "2027-02-11", "Dorada", 27.90, 12)
        )
        branches[3].inventory.add_product(
            Product("Pollo", "1000000022", "Proteinas", "2026-01-22", "Granjita", 36.00, 15)
        )
        branches[3].inventory.add_product(
            Product("Lechuga", "1000000023", "Verduras", "2026-02-08", "Fresco", 3.95, 34)
        )

    if len(branches) >= 5:
        branches[4].inventory.add_product(
            Product("Cereal", "1000000007", "Desayuno", "2026-06-01", "Crunchy", 18.50, 22)
        )
        branches[4].inventory.add_product(
            Product("Sopa", "1000000024", "Enlatados", "2027-06-20", "Casera", 7.80, 48)
        )
        branches[4].inventory.add_product(
            Product("Agua", "1000000025", "Bebidas", "2027-12-31", "PuraVida", 4.00, 90)
        )
        branches[4].inventory.add_product(
            Product("Jabon", "1000000026", "Higiene", "2027-07-07", "Limpio", 6.50, 36)
        )
        branches[4].inventory.add_product(
            Product("Papas", "1000000027", "Snacks", "2026-04-17", "Crujientes", 10.25, 44)
        )
