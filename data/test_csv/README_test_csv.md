# Test CSV datasets for supermarket_inventory_system

Folders:
- basic: small valid dataset for quick demonstrations.
- stress_1000: valid dataset with 1,000 products for larger tests.
- errors: invalid datasets for CSV validation and errors.log demonstration.

Load order:
1. branches_*.csv
2. connections_*.csv
3. products_*.csv

Expected valid loads:
- basic: 3 branches, 3 connections, 12 products.
- stress_1000: 5 branches, 6 connections, 1000 products.


Notes:
- Product barcodes are 10 digits.
- Some fields include commas inside quotes, for example "Fruits Company, Inc.".
- The errors folder intentionally includes bad rows.

---

Usage:
- Use `basic/` + `errors/`.
- Use `stress_1000/`.

Scenarios:
- basic: normal functionality.
- errors: validation at erros.log.
- stress_1000: big data load.

---
