import base64
import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Libro'
    _order = 'name'

    # Tamaño máximo permitido para la portada (en bytes).
    _MAX_IMAGE_BYTES = 2 * 1024 * 1024  # 2 MB

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
    # Género gestionado como modelo propio (library.genre): la empresa puede
    # dar de alta/baja géneros y se comparten con los clientes.
    genre_id = fields.Many2one('library.genre', string='Género')
    description = fields.Text(string='Descripción')
    # Binary con max_width/height para que Odoo genere miniaturas automáticamente
    image = fields.Image(string='Portada', max_width=1920, max_height=1920)
    image_small = fields.Image(string='Portada pequeña', related='image', max_width=128, max_height=128, store=True)
    # El estado se calcula a partir del stock y del flag de descatalogado:
    # ya no se marca "sin stock" a mano (no tendría sentido teniendo el stock).
    discontinued = fields.Boolean(string='Descatalogado', default=False, copy=False)
    state = fields.Selection([
        ('for_sale', 'En venta'),
        ('out_of_stock', 'Sin stock'),
        ('discontinued', 'Descatalogado'),
    ], string='Estado', compute='_compute_state', store=True)
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
    # Número de tiendas con este libro por debajo de su stock mínimo.
    below_minimum_count = fields.Integer(
        string='Tiendas bajo mínimo', compute='_compute_below_minimum_count', store=True)

    @api.depends('stock_ids.quantity')
    def _compute_stock_total(self):
        for record in self:
            record.stock_total = sum(record.stock_ids.mapped('quantity'))

    @api.depends('stock_ids.below_minimum')
    def _compute_below_minimum_count(self):
        for record in self:
            record.below_minimum_count = len(record.stock_ids.filtered('below_minimum'))

    @api.depends('stock_total', 'discontinued')
    def _compute_state(self):
        # discontinued (manual) tiene prioridad; si no, el estado depende del stock.
        for book in self:
            if book.discontinued:
                book.state = 'discontinued'
            elif book.stock_total <= 0:
                book.state = 'out_of_stock'
            else:
                book.state = 'for_sale'

    def action_discontinue(self):
        # Descataloga el libro (lo retira del catálogo de venta).
        for book in self:
            book.discontinued = True

    def action_undiscontinue(self):
        # Vuelve a poner el libro en el catálogo.
        for book in self:
            book.discontinued = False

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

    @api.constrains('image')
    def _check_image_size(self):
        # Comprobación real del tamaño de la portada: rechaza imágenes pesadas.
        for record in self:
            if record.image:
                try:
                    size = len(base64.b64decode(record.image))
                except Exception:
                    size = 0
                if size > self._MAX_IMAGE_BYTES:
                    raise ValidationError(
                        'La portada no puede superar los 2 MB (tamaño actual: %.1f MB).'
                        % (size / (1024 * 1024))
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
