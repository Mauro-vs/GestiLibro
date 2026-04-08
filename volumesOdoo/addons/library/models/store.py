from odoo import models, fields


class LibraryStore(models.Model):
    _name = 'library.store'
    _description = 'Tienda'

    name = fields.Char(string='Nombre', required=True)
    address = fields.Char(string='Dirección')
    responsible_id = fields.Many2one('res.partner', string='Responsable')


class LibraryStock(models.Model):
    _name = 'library.stock'
    _description = 'Stock por tienda'

    book_id = fields.Many2one('library.book', string='Libro', required=True)
    store_id = fields.Many2one('library.store', string='Tienda', required=True)
    quantity = fields.Integer(string='Cantidad', default=0)
    quantity_minimum = fields.Integer(string='Cantidad mínima', default=0)
