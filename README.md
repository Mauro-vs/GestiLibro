# Biblioteca (módulo Odoo)

Módulo Odoo `library` para gestionar libros, autores, tiendas y stock.

Instalación rápida:

1. Copiar la carpeta `library` dentro del `addons` de tu instancia de Odoo (por ejemplo, en `volumesOdoo/addons`).
2. Reiniciar el servidor de Odoo o recargar los addons.
3. Actualizar la lista de aplicaciones e instalar el módulo "Biblioteca".

Archivos creados:

- `models/` : modelos `book`, `author`, `store`, `stock`, `publisher`, `order`.
- `views/` : vistas tree/form y menús básicos.
- `security/` : grupo y `ir.model.access.csv`.
- `data/` : datos de ejemplo.

Recientes añadidos:

- `publisher` (editorial): modelo `library.publisher`, vistas y demo.
- Pedidos de venta: `library.order` y `library.order.line` con `cliente` como `res.partner` y líneas vinculadas a `library.book`.

Pruebas rápidas:

1. Copiar la carpeta `library` dentro del `addons` de tu instancia de Odoo.
2. Reiniciar el servidor de Odoo o recargar los addons.
3. Actualizar la lista de aplicaciones e instalar el módulo "Biblioteca".
4. En el menú `Biblioteca` verás: Libros, Autores, Editoriales, Tiendas, Pedidos.
5. Los datos demo incluyen un autor y una editorial; crea un `partner` y prueba crear un pedido.
