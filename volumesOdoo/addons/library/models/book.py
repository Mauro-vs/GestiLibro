import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Libro'

    # Reglas de integridad basicas: ISBN unico y precios no negativos.
    _sql_constraints = [
        ('library_book_isbn_uniq', 'unique(isbn)', 'El ISBN debe ser unico.'),
        ('library_book_price_sale_nonneg', 'CHECK(price_sale >= 0)', 'El precio de venta debe ser positivo.'),
        ('library_book_price_cost_nonneg', 'CHECK(price_cost >= 0)', 'El precio de coste debe ser positivo.'),
    ]

    # Campos principales del catalogo de libros.
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
    # Stock total agregado desde los registros de stock por tienda.
    stock_total = fields.Integer(string='Stock total', compute='_compute_stock_total', store=True)

    @api.depends('stock_ids.quantity')
    def _compute_stock_total(self):
        # Suma el stock de todas las tiendas para mostrar un total.
        # Nota: al usar `store=True` esto se guarda en BD y puede quedar
        # desincronizado si hay operaciones fuera del ORM o concurrencia.
        for record in self:
            record.stock_total = sum(record.stock_ids.mapped('quantity'))

    @api.constrains('publication_year')
    def _check_publication_year(self):
        # Evita años fuera de rango razonable en el catálogo.
        # Comentario práctico: protege contra entradas con errores tipográficos
        # (p. ej. 3000) y libros anteriores a la imprenta moderna.
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
        # Regla comercial simple: el precio de venta no debe ser menor al coste.
        # Explicación: usamos `ValidationError` para dar feedback legible al usuario
        # y para permitir lógicas más complejas que no pueden expresarse en SQL.
        for record in self:
            if (
                record.price_sale is not False
                and record.price_cost is not False
                and record.price_sale < record.price_cost
            ):
                raise ValidationError(
                    'El precio de venta no puede ser menor que el precio de coste.'
                )
