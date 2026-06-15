from odoo import models, fields, api


class LibraryStore(models.Model):
    _name = 'library.store'
    _description = 'Tienda'
    _order = 'name'

    # Datos basicos de la tienda.
    name = fields.Char(string='Nombre', required=True)
    address = fields.Char(string='Dirección')
    # Responsable de la tienda: es un usuario de Odoo (no un contacto) porque
    # se usa en las reglas de registro para que gestione solo SU tienda.
    responsible_id = fields.Many2one('res.users', string='Responsable', required=True)
    stock_ids = fields.One2many('library.stock', 'store_id', string='Stock')
    order_ids = fields.One2many('library.order', 'store_id', string='Ventas')
    below_minimum_count = fields.Integer(
        string='Referencias bajo mínimo', compute='_compute_below_minimum_count')

    @api.depends('stock_ids.below_minimum')
    def _compute_below_minimum_count(self):
        for store in self:
            store.below_minimum_count = len(store.stock_ids.filtered('below_minimum'))


class LibraryStock(models.Model):
    _name = 'library.stock'
    _description = 'Stock por tienda'

    # Reglas de integridad para evitar duplicados y valores negativos.
    _sql_constraints = [
        (
            'library_stock_book_store_uniq',
            'unique(book_id, store_id)',
            'Ya existe un registro de stock para este libro en esta tienda.',
        ),
        (
            'library_stock_quantity_nonneg',
            'CHECK(quantity >= 0)',
            'La cantidad debe ser positiva.',
        ),
        (
            'library_stock_quantity_minimum_nonneg',
            'CHECK(quantity_minimum >= 0)',
            'La cantidad minima debe ser positiva.',
        ),
    ]

    # Relacion libro-tienda y cantidades de stock.
    book_id = fields.Many2one('library.book', string='Libro', required=True)
    store_id = fields.Many2one('library.store', string='Tienda', required=True)
    quantity = fields.Integer(string='Cantidad', default=0)
    quantity_minimum = fields.Integer(string='Cantidad mínima', default=0)
    # Marca cuándo una tienda está por debajo de su stock mínimo para ese libro.
    below_minimum = fields.Boolean(
        string='Bajo mínimo', compute='_compute_below_minimum', store=True)

    @api.depends('quantity', 'quantity_minimum')
    def _compute_below_minimum(self):
        for stock in self:
            stock.below_minimum = stock.quantity < stock.quantity_minimum
