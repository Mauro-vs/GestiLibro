{
    'name': 'GestiLibros',
    'version': '18.0.2.0.0',
    'summary': 'Gestión de tiendas de libros: catálogo, stock y ventas',
    'description': """
GestiLibros

Modulo de gestion integral para una cadena de tiendas de libros.

Funcionalidades principales:

- Catalogo de libros con portada, ISBN, genero configurable, precios, autores y editorial.
- Autores con foto y vista Kanban, y editoriales, con pais basado en res.country.
- Stock independiente por tienda, con cantidad minima y aviso de stock bajo minimo.
- Proceso de venta con validacion y descuento automatico de stock.
- Facturacion automatica integrada con Contabilidad: la factura se genera y se confirma al cerrar la venta.
- Clientes (extension de res.partner) con codigo automatico, genero favorito y puntos de fidelidad.
- Tres roles asignables (Consulta, Vendedor y Gestor) con aislamiento por tienda.

Depende de los modulos base y account (Contabilidad).
""",
    'author': 'Mauro Valdés Sanjuan',
    'website': 'https://github.com/',
    'license': 'LGPL-3',
    'category': 'Sales',
    # account necesario para crear facturas con account.move
    'depends': ['base', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/library_sequence.xml',
        'data/library_data.xml',
        'views/library_genre_views.xml',
        'views/library_partner_views.xml',
        'views/library_book_views.xml',
        'views/library_author_views.xml',
        'views/library_publisher_views.xml',
        'views/library_store_views.xml',
        'views/library_order_views.xml',
        'views/library_account_move_views.xml',
        'views/library_menu.xml',
    ],
    'images': ['static/description/icon.png'],
    'application': True,
    'installable': True,
}
