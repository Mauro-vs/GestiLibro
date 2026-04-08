from odoo import models, fields


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Libro'
    name = fields.Char(string='Título', required=True)
    isbn = fields.Char(string='ISBN')
    publication_year = fields.Integer(string='Año de publicación')
    price_sale = fields.Monetary(string='Precio de venta')
    price_cost = fields.Monetary(string='Precio de coste')
    currency_id = fields.Many2one('res.currency', string='Moneda')
    genre = fields.Char(string='Género')
    state = fields.Selection([
        ('available', 'Disponible'),
        ('borrowed', 'Prestado'),
        ('lost', 'Perdido')
    ], default='available')
    publisher_id = fields.Many2one('library.publisher', string='Editorial')
    author_ids = fields.Many2many('library.author', string='Autores')
