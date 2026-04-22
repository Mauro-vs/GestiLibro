from odoo import models, fields, api


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Libro'

    name = fields.Char(string='Título', required=True)
    isbn = fields.Char(string='ISBN')
    publication_year = fields.Integer(string='Año de publicación')
    price_sale = fields.Monetary(string='Precio de venta')
    price_cost = fields.Monetary(string='Precio de coste')
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )
    genre = fields.Char(string='Género')
    state = fields.Selection([
        ('for_sale', 'En venta'),
        ('out_of_stock', 'Sin stock'),
        ('discontinued', 'Descatalogado'),
    ], default='for_sale')
    publisher_id = fields.Many2one('library.publisher', string='Editorial')
    author_ids = fields.Many2many(
        'library.author',
        'library_book_author_rel',
        'book_id',
        'author_id',
        string='Autores',
    )
    stock_ids = fields.One2many('library.stock', 'book_id', string='Stock por tienda')
    order_line_ids = fields.One2many('library.order.line', 'book_id', string='Líneas de venta')
    stock_total = fields.Integer(string='Stock total', compute='_compute_stock_total', store=True)

    @api.depends('stock_ids.quantity')
    def _compute_stock_total(self):
        for record in self:
            record.stock_total = sum(record.stock_ids.mapped('quantity'))
