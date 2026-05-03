import time


class InventoryProcessingService:
    @staticmethod
    def get_sample(products, n):
        if n is None or n <= 0:
            return products[:]

        return products[:min(n, len(products))]

    @staticmethod
    def sequential_search(products, query):
        query = query.lower()
        return [
            product for product in products
            if query in product.name.lower()
            or query in product.barcode.lower()
            or query in product.category.lower()
        ]

    @staticmethod
    def search_by_name(products, query):
        query = query.lower()
        return [
            product for product in products
            if query in product.name.lower()
        ]

    @staticmethod
    def search_by_barcode(products, query):
        products_by_barcode = {product.barcode: product for product in products}
        product = products_by_barcode.get(query)

        if product is not None:
            return [product]

        return [
            product for product in products
            if query in product.barcode
        ]

    @staticmethod
    def search_by_category(products, query):
        query = query.lower()
        return [
            product for product in products
            if query in product.category.lower()
        ]

    @staticmethod
    def binary_search_by_name(products, query):
        sorted_products = sorted(products, key=lambda product: product.name.lower())
        left = 0
        right = len(sorted_products) - 1
        query = query.lower()

        while left <= right:
            middle = (left + right) // 2
            product_name = sorted_products[middle].name.lower()

            if product_name == query:
                return [sorted_products[middle]]
            if product_name < query:
                left = middle + 1
            else:
                right = middle - 1

        return []

    @staticmethod
    def hash_search_by_barcode(products, query):
        products_by_barcode = {product.barcode: product for product in products}
        product = products_by_barcode.get(query)
        return [product] if product is not None else []

    @staticmethod
    def search_linked_list_structure(inventory, query):
        result = inventory.unordered_list.search_by_name(query)
        return [] if result is None else [result]

    @staticmethod
    def search_avl_structure(inventory, query):
        result = inventory.avl_tree.search(query)
        return [] if result is None else [result]

    @staticmethod
    def search_hash_structure(inventory, query):
        result = inventory.hash_table.search(query)
        return [] if result is None else [result]

    @classmethod
    def benchmark_search_methods(cls, inventory, n=20, m=5):
        products = inventory.get_all_products()

        if not products:
            return []

        total_products = len(products)
        requested_queries = max(1, n)
        executed_success_queries = min(requested_queries, total_products)

        first_product = products[0]
        last_product = products[-1]

        # Select successful queries spread across the whole inventory
        # This avoids favoring sequential search by only using the first N products
        success_products = []
        if executed_success_queries == 1:
            success_products.append(first_product)
        else:
            for index in range(executed_success_queries):
                product_index = round(index * (total_products - 1) / (executed_success_queries - 1))
                success_products.append(products[product_index])

        cases = {
            "Éxito distribuido": success_products,
            "Fallida": [None] * requested_queries,
            "Extremo primero": [first_product] * requested_queries,
            "Extremo último": [last_product] * requested_queries,
        }

        methods = {
            "Lista enlazada": lambda product: cls.search_linked_list_structure(
                inventory,
                "NO_EXISTE_PRODUCTO" if product is None else product.name
            ),
            "AVL por nombre": lambda product: cls.search_avl_structure(
                inventory,
                "NO_EXISTE_PRODUCTO" if product is None else product.name
            ),
            "Hash por código": lambda product: cls.search_hash_structure(
                inventory,
                "0000000000" if product is None else product.barcode
            ),
        }

        results = []
        repetitions = max(1, m)

        for case_name, case_products in cases.items():
            for method_name, method_callback in methods.items():
                total_time = 0

                for _ in range(repetitions):
                    start_time = time.perf_counter()

                    for product in case_products:
                        method_callback(product)

                    total_time += (time.perf_counter() - start_time) * 1000

                total_queries = repetitions * len(case_products)
                avg_time = total_time / total_queries if total_queries > 0 else 0

                results.append({
                    "operation": "Búsqueda",
                    "case": case_name,
                    "method": method_name,
                    "requested_n": requested_queries,
                    "executed_queries": len(case_products),
                    "available_products": total_products,
                    "m": repetitions,
                    "average_ms": avg_time,
                })

        return results

    @classmethod
    def search_products(cls, products, query, method="name"):
        start_time = time.perf_counter()

        if method == "barcode":
            found_products = cls.search_by_barcode(products, query)
        elif method == "category":
            found_products = cls.search_by_category(products, query)
        elif method == "binary":
            found_products = cls.binary_search_by_name(products, query)
        elif method == "hash":
            found_products = cls.hash_search_by_barcode(products, query)
        elif method == "sequential":
            found_products = cls.sequential_search(products, query)
        else:
            found_products = cls.search_by_name(products, query)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return found_products, elapsed_ms

    @staticmethod
    def format_benchmark_results(results):
        if not results:
            return "No hay resultados de rendimiento"

        lines = []

        for result in results:
            average_us = result["average_ms"] * 1000
            base = (
                f"{result['operation']} | {result['case']} | {result['method']} | "
                f"N solicitado={result['requested_n']} | "
                f"Consultas={result['executed_queries']} | "
                f"Productos={result['available_products']} | "
                f"M={result['m']} | "
                f"Promedio={average_us:.2f} μs"
            )

            lines.append(base)

        return "\n".join(lines)