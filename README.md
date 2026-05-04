# Supermarket Inventory System

Sistema de inventario y transferencias entre sucursales que utiliza estructuras de datos (AVL, Hash, B+, B-Tree) y simulación con hilos para optimizar búsquedas y logística.

---

## 🚀 Requisitos
- Python 3.10+
- (Opcional) Graphviz instalado en el sistema

---

## ⚙️ Instalación
```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\\Scripts\\activate    # Windows

pip install -r requirements.txt
```

---

## ▶️ Ejecución
Desde la raíz del proyecto:
```bash
python main.py
```

Opcional, si se genera ejecutable con PyInstaller en macOS:
```bash
open dist/main.app
```

También puede ejecutarse el binario directo:
```bash
./dist/main
```

---

## 📦 Generar ejecutable opcional
Desde la raíz del proyecto:
```bash
pyinstaller --onefile --windowed --add-data "app/gui/main_window.ui:app/gui" --add-data "data:data" main.py
```

El resultado queda en:
```text
dist/main.app
```

---

## 📁 Uso rápido (CSV)
Cargar en este orden:
1. Sucursales
2. Conexiones
3. Productos

Datasets incluidos:
- `data/test_csv/basic` → demo
- `data/test_csv/errors` → validación
- `data/test_csv/stress_1000` → rendimiento (cargar aparte)

---

## 🔑 Funcionalidades principales
- Búsquedas:
  - Nombre → AVL
  - Código → Hash
  - Categoría → B+ Tree
  - Fecha (rango) → B-Tree
- Transferencias con hilos (QThread) y colas FIFO por sucursal
- Visualización de grafos y estructuras
- Exportación a SVG/PNG
- Validación de CSV con registro en `errors.log`

---

## 🧪 Notas
- Para demo: usar `basic + errors` juntos.
- Para rendimiento: usar `stress_1000` en sesión limpia.

---

## 📚 Documentación
- Reporte técnico: ver *Report.md*
- Manual de usuario: ver *UserManual.md*