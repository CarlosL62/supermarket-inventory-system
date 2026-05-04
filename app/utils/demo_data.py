from app.models.branch import Branch
from app.models.product import Product


def load_demo_branches(branch_manager):
    branch_manager.add_branch(Branch(1, "Central", "Zona 1", 20, 18, 25))
    branch_manager.add_branch(Branch(2, "Norte", "Zona 5", 18, 15, 22))
    branch_manager.add_branch(Branch(3, "Sur", "Zona 12", 22, 20, 28))
    branch_manager.add_branch(Branch(4, "Occidente", "Zona 7", 25, 22, 30))
    branch_manager.add_branch(Branch(5, "Sin conexión", "Zona 18", 16, 14, 20))
    branch_manager.add_branch(Branch(6, "Pruebas Árboles", "Zona 10", 18, 16, 24))
    branch_manager.add_branch(Branch(7, "Carga 500", "Zona 15", 20, 18, 26))

    branch_manager.connect_branches(1, 2, 45, 3, True)
    branch_manager.connect_branches(1, 3, 35, 9, True)
    branch_manager.connect_branches(3, 2, 28, 8, True)
    branch_manager.connect_branches(2, 4, 40, 2, True)
    branch_manager.connect_branches(3, 4, 30, 10, True)
    branch_manager.connect_branches(1, 7, 38, 4, True)
    branch_manager.connect_branches(7, 4, 42, 6, True)

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

    if len(branches) >= 6:
        branches[5].inventory.add_product(
            Product("Almendras", "1000000028", "Snacks", "2026-01-05", "NutriMix", 18.25, 30)
        )
        branches[5].inventory.add_product(
            Product("Brocoli", "1000000029", "Verduras", "2026-01-12", "Fresco", 6.40, 26)
        )
        branches[5].inventory.add_product(
            Product("Chocolate", "1000000030", "Snacks", "2026-01-19", "DulceHogar", 11.75, 24)
        )
        branches[5].inventory.add_product(
            Product("Durazno", "1000000031", "Frutas", "2026-01-26", "DelCampo", 5.90, 34)
        )
        branches[5].inventory.add_product(
            Product("Espinaca", "1000000032", "Verduras", "2026-02-02", "Fresco", 4.80, 40)
        )
        branches[5].inventory.add_product(
            Product("Fideos", "1000000033", "Despensa", "2026-02-09", "LaItaliana", 7.35, 55)
        )
        branches[5].inventory.add_product(
            Product("Granola", "1000000034", "Desayuno", "2026-02-16", "NaturalFit", 16.20, 22)
        )
        branches[5].inventory.add_product(
            Product("Harina", "1000000035", "Despensa", "2026-02-23", "Molino", 9.10, 60)
        )
        branches[5].inventory.add_product(
            Product("Ice Tea", "1000000036", "Bebidas", "2026-03-02", "BuenDia", 8.95, 28)
        )
        branches[5].inventory.add_product(
            Product("Jalea", "1000000037", "Despensa", "2026-03-09", "Dorada", 13.50, 18)
        )
        branches[5].inventory.add_product(
            Product("Kiwi", "1000000038", "Frutas", "2026-03-16", "DelCampo", 6.85, 32)
        )
        branches[5].inventory.add_product(
            Product("Lentejas", "1000000039", "Granos", "2026-03-23", "Chapines", 10.40, 48)
        )
        branches[5].inventory.add_product(
            Product("Mantequilla", "1000000040", "Lacteos", "2026-03-30", "LaVaquita", 14.75, 20)
        )
        branches[5].inventory.add_product(
            Product("Nueces", "1000000041", "Snacks", "2026-04-06", "NutriMix", 21.60, 16)
        )
        branches[5].inventory.add_product(
            Product("Oregano", "1000000042", "Condimentos", "2026-04-13", "SazonMax", 5.25, 35)
        )
        branches[5].inventory.add_product(
            Product("Pepino", "1000000043", "Verduras", "2026-04-20", "Fresco", 3.70, 45)
        )
        branches[5].inventory.add_product(
            Product("Quinoa", "1000000044", "Granos", "2026-04-27", "NaturalFit", 24.30, 14)
        )
        branches[5].inventory.add_product(
            Product("Repollo", "1000000045", "Verduras", "2026-05-04", "Fresco", 4.10, 39)
        )
        branches[5].inventory.add_product(
            Product("Sardinas", "1000000046", "Enlatados", "2026-05-11", "MarAzul", 10.95, 31)
        )
        branches[5].inventory.add_product(
            Product("Tortillas", "1000000047", "Panaderia", "2026-05-18", "LaMesa", 6.15, 52)
        )
        branches[5].inventory.add_product(
            Product("Uvas", "1000000048", "Frutas", "2026-05-25", "DelCampo", 12.80, 27)
        )
        branches[5].inventory.add_product(
            Product("Vinagre", "1000000049", "Condimentos", "2026-06-01", "SazonMax", 7.90, 33)
        )
        branches[5].inventory.add_product(
            Product("Waffles", "1000000050", "Desayuno", "2026-06-08", "Crunchy", 15.40, 21)
        )
        branches[5].inventory.add_product(
            Product("Yuca", "1000000051", "Verduras", "2026-06-15", "Fresco", 5.60, 36)
        )
        branches[5].inventory.add_product(
            Product("Zanahoria", "1000000052", "Verduras", "2026-06-22", "Fresco", 4.30, 42)
        )

    if len(branches) >= 7:
        benchmark_categories = [
            "Abarrotes", "Bebidas", "Carnes", "Congelados", "Despensa",
            "Enlatados", "Frutas", "Higiene", "Lacteos", "Limpieza",
            "Panaderia", "Proteinas", "Snacks", "Verduras"
        ]
        benchmark_brands = [
            "MarcaA", "MarcaB", "MarcaC", "MarcaD", "MarcaE",
            "MarcaF", "MarcaG", "MarcaH", "MarcaI", "MarcaJ"
        ]

        for index in range(500):
            product_number = index + 1
            category = benchmark_categories[index % len(benchmark_categories)]
            brand = benchmark_brands[index % len(benchmark_brands)]
            month = (index % 12) + 1
            day = (index % 28) + 1
            expiry_date = f"2027-{month:02d}-{day:02d}"
            barcode = f"{2000000000 + product_number:010d}"
            price = round(5.00 + (index % 95) * 0.75, 2)
            stock = 10 + (index % 90)

            branches[6].inventory.add_product(
                Product(
                    f"Producto Benchmark {product_number:03d}",
                    barcode,
                    category,
                    expiry_date,
                    brand,
                    price,
                    stock
                )
            )
