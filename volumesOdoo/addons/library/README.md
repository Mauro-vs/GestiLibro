# GestiLibros — Módulo Odoo

Módulo Odoo para gestionar una red de librerías independiente. Cubre catálogo de libros, autores, editoriales, stock por tienda, ventas y facturación automática.

---

## Instalación

**Requisitos:** Odoo 17 · Docker (recomendado)

### Con Docker

```bash
git clone <url-del-repositorio>
cd GestiLibros
docker compose up -d
```

Accede a `http://localhost:8069`, crea una base de datos e instala el módulo **GestiLibros** desde Aplicaciones.

### Manual

1. Copia la carpeta `library/` dentro del directorio `addons` de tu instancia Odoo.
2. Reinicia el servidor: `./odoo-bin -u library -d <nombre_bd>`.
3. En Ajustes → Aplicaciones, busca **GestiLibros** e instálalo.

> El módulo depende de `account` (Contabilidad). Asegúrate de tenerlo instalado.

---

## Funcionalidades

### Catálogo de libros
- Ficha completa: título, ISBN, año, género (Selection), descripción y portada (imagen).
- Relación con autores (Many2many) y editorial (Many2one).
- Stock total calculado automáticamente a partir del stock por tienda.
- Estado del libro: **En venta**, **Sin stock**, **Descatalogado** con barra de estado visual.
- Botones de acción rápida: *Marcar como agotado* / *Volver a en venta*.
- Vista **Kanban** agrupada por género, con portada, autores, precio y badge de estado.

### Autores y editoriales
- Autores con nombre, nacionalidad, fecha de nacimiento y biografía breve.
- Editoriales con nombre, país, web y teléfono.

### Tiendas y stock
- Gestión de varias tiendas con nombre, dirección y responsable.
- Stock por tienda con cantidad disponible y cantidad mínima de reposición.

### Ventas y pedidos
- Pedidos con referencia automática secuencial (`ORD/2026/0001`).
- Flujo de estados: Borrador → Confirmado → Hecho / Cancelado.
- Validación de stock antes de confirmar (por tienda y por libro).
- Descuento automático de stock al confirmar.
- Precio unitario autocompletado al seleccionar un libro (`onchange`).
- Total del pedido calculado en tiempo real.

### Facturación automática
- Al confirmar un pedido se genera automáticamente una factura de cliente en el módulo de **Contabilidad** (`account.move`).
- Botón *Ver factura* para acceder directamente desde el pedido.

### Clientes (herencia de res.partner)
- Campos propios: código de cliente, género favorito, puntos de fidelidad.
- Contador de ventas confirmadas con acceso directo desde la ficha.
- Historial de pedidos integrado en la pestaña GestiLibros.

### Seguridad
- **Usuario de librería**: acceso de lectura al catálogo.
- **Gestor de librería**: acceso completo a tiendas, ventas y clientes. Hereda los permisos de usuario.

---

## Estructura del módulo

```
library/
├── __manifest__.py
├── models/
│   ├── book.py          # library.book — catálogo de libros
│   ├── author.py        # library.author — autores
│   ├── publisher.py     # library.publisher — editoriales
│   ├── store.py         # library.store + library.stock
│   ├── order.py         # library.order — pedidos de venta
│   ├── order_line.py    # library.order.line — líneas de pedido
│   └── partner.py       # herencia de res.partner
├── views/
│   ├── library_book_views.xml
│   ├── library_author_views.xml
│   ├── library_publisher_views.xml
│   ├── library_store_views.xml
│   ├── library_order_views.xml
│   ├── library_partner_views.xml
│   └── library_menu.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
└── data/
    ├── library_sequence.xml   # secuencia ORD/YYYY/XXXX
    └── library_data.xml       # datos demo (12 libros, 3 tiendas, 6 clientes)
```

---

## Prueba rápida

1. Instala el módulo. Los datos demo se cargan automáticamente.
2. Ve a **GestiLibros → Catálogo → Libros** y comprueba la vista kanban.
3. Crea una venta en **Gestión → Ventas**: selecciona tienda, cliente y añade líneas.
4. Pulsa **Confirmar** — se descuenta el stock y se genera la factura automáticamente.
5. Pulsa **Ver factura** para acceder a la factura desde el pedido.
