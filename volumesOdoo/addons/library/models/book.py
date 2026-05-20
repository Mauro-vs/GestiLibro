import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Libro'

    _sql_constraints = [
        ('library_book_isbn_uniq', 'unique(isbn)', 'El ISBN debe ser unico.'),
        ('library_book_price_sale_nonneg', 'CHECK(price_sale >= 0)', 'El precio de venta debe ser positivo.'),
        ('library_book_price_cost_nonneg', 'CHECK(price_cost >= 0)', 'El precio de coste debe ser positivo.'),
    ]

    name = fields.Char(string='Título', required=True)
    isbn = fields.Char(string='ISBN', required=True)
    publication_year = fields.Integer(string='Año de publicación')
    price_sale = fields.Monetary(string='Precio de venta')
    price_cost = fields.Monetary(string='Precio de coste')
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )
    # genre cambiado a Selection para limitar los valores posibles
    genre = fields.Selection([
        ('fiction', 'Ficción'),
        ('non_fiction', 'No ficción'),
        ('children', 'Infantil'),
        ('comic', 'Cómic'),
        ('science', 'Ciencia'),
        ('history', 'Historia'),
        ('biography', 'Biografía'),
        ('other', 'Otro'),
    ], string='Género')
    description = fields.Text(string='Descripción')
    # Binary con max_width/height para que Odoo genere miniaturas automáticamente
    image = fields.Image(string='Portada', max_width=1024, max_height=1024)
    image_small = fields.Image(string='Portada pequeña', related='image', max_width=128, max_height=128, store=True)
    state = fields.Selection([
        ('for_sale', 'En venta'),
        ('out_of_stock', 'Sin stock'),
        ('discontinued', 'Descatalogado'),
    ], default='for_sale', string='Estado')
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

    def action_mark_out_of_stock(self):
        # Botón de acción rápida para marcar libros como sin stock.
        # Se puede llamar desde el formulario o desde la lista (acción masiva).
        for book in self:
            book.state = 'out_of_stock'

    def action_mark_for_sale(self):
        # Reactiva un libro para venta si tenía stock o estaba descatalogado.
        for book in self:
            book.state = 'for_sale'

    @api.constrains('publication_year')
    def _check_publication_year(self):
        current_year = datetime.date.today().year
        for record in self:
            if record.publication_year and (
                record.publication_year < 1450 or record.publication_year > current_year
            ):
                raise ValidationError(
                    'El año de publicación debe estar entre 1450 y %s.' % current_year
                )

    @api.constrains('price_sale', 'price_cost')
    def _check_price_margin(self):
        # El precio de venta no puede ser menor al coste: regla comercial básica.
        for record in self:
            if (
                record.price_sale is not False
                and record.price_cost is not False
                and record.price_sale < record.price_cost
            ):
                raise ValidationError(
                    'El precio de venta no puede ser menor que el precio de coste.'
                )
