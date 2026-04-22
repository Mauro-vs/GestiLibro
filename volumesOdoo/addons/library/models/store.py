from odoo import models, fields


class LibraryStore(models.Model):
    _name = 'library.store'
    _description = 'Tienda'

    name = fields.Char(string='Nombre', required=True)
    address = fields.Char(string='Dirección')
    responsible_id = fields.Many2one('res.partner', string='Responsable')
    stock_ids = fields.One2many('library.stock', 'store_id', string='Stock')
    order_ids = fields.One2many('library.order', 'store_id', string='Ventas')


class LibraryStock(models.Model):
    _name = 'library.stock'
    _description = 'Stock por tienda'

    _sql_constraints = [
        (
            'library_stock_book_store_uniq',
            'unique(book_id, store_id)',
            'Ya existe un registro de stock para este libro en esta tienda.',
        )
    ]

    book_id = fields.Many2one('library.book', string='Libro', required=True)
    store_id = fields.Many2one('library.store', string='Tienda', required=True)
    quantity = fields.Integer(string='Cantidad', default=0)
    quantity_minimum = fields.Integer(string='Cantidad mínima', default=0)
