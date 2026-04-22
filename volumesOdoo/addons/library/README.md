# GestiLibros (módulo Odoo)

Módulo Odoo para gestionar una red de tiendas de libros, con catálogo, stock y ventas.

## Qué incluye

- Libros, autores y editoriales.
- Tiendas y stock por tienda.
- Ventas con líneas de venta por libro.
- Vistas list/form y menús de catálogo y gestión.
- Seguridad por grupos (usuario, vendedor, gestor).

## Relaciones principales

- Un libro puede tener varios autores y una editorial.
- Una tienda tiene múltiples líneas de stock y ventas.
- Una venta pertenece a una tienda y a un cliente.
- Una venta tiene líneas de venta asociadas a libros.

## Instalación rápida

1. Copia la carpeta library dentro del addons de tu instancia Odoo.
2. Reinicia Odoo o recarga addons.
3. Actualiza la lista de aplicaciones e instala GestiLibros.

## Prueba básica

1. Crea una tienda.
2. Crea uno o varios libros.
3. Asigna stock del libro en la tienda.
4. Crea una venta con cliente, tienda y líneas de venta.
