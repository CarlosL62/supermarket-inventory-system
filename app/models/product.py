class Product:
    def __init__(self, name, barcode, category, expiry_date, brand, price, stock):
        self.name = name
        self.barcode = barcode
        self.category = category
        self.expiry_date = expiry_date
        self.brand = brand
        self.price = price
        self.stock = stock

    def __repr__(self):
        return (
            f"Product(name='{self.name}', barcode='{self.barcode}', "
            f"category='{self.category}', expiry_date='{self.expiry_date}', "
            f"brand='{self.brand}', price={self.price}, stock={self.stock})"
        )