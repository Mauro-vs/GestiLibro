# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LibraryOrder(models.Model):
    _name = 'library.order'
    _description = 'Venta'
    _order = 'date desc, id desc'

    # Datos basicos de la venta y del cliente.
    name = fields.Char(string='Referencia', readonly=True, default='New')
    store_id = fields.Many2one('library.store', string='Tienda', required=True)
    client_id = fields.Many2one('res.partner', string='Cliente', required=True)
    # Campos relacionados para facilitar búsquedas y filtros desde la orden.
    client_is_library_customer = fields.Boolean(
        string='Cliente GestiLibros',
        related='client_id.is_library_customer',
        readonly=True,
        store=True,
    )
    client_library_customer_code = fields.Char(
        string='Codigo cliente',
        related='client_id.library_customer_code',
        readonly=True,
        store=True,
    )
    # Estado de la venta y lineas asociadas.
    date = fields.Datetime(string='Fecha', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('done', 'Hecho'),
        ('cancel', 'Cancelado')
    ], default='draft')
    line_ids = fields.One2many('library.order.line', 'order_id', string='Líneas de venta', copy=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )
    amount_total = fields.Monetary(string='Total', compute='_compute_amount_total', store=True, readonly=True)

    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        # Total de la venta sumando subtotales de lineas.
        for record in self:
            record.amount_total = sum(record.line_ids.mapped('price_subtotal'))

    def action_confirm(self):
        # Accion de flujo: valida y confirma una venta.
        # Comentario: validar stock antes de consumirlo evita ventas sin stock.
        for order in self:
            if not order.line_ids:
                raise ValidationError('No puedes confirmar una venta sin lineas.')
            order._check_stock_available()
            order._consume_stock()
            order.state = 'confirmed'

    def action_done(self):
        # Marca como hecha y consume stock si venia en borrador.
        for order in self:
            if order.state == 'draft':
                if not order.line_ids:
                    raise ValidationError('No puedes confirmar una venta sin lineas.')
                order._check_stock_available()
                order._consume_stock()
            order.state = 'done'

    def action_cancel(self):
        # Cancela la venta sin modificar stock (se mantiene la decision actual).
        for order in self:
            order.state = 'cancel'

    def action_reset_draft(self):
        # Devuelve a borrador para re-editar la venta.
        for order in self:
            order.state = 'draft'

    def _get_qty_by_book(self):
        # Agrupa cantidades por libro para validar stock en ventas con lineas repetidas.
        # Explicación: si un pedido tiene dos líneas del mismo libro, sumamos
        # las cantidades para hacer una única comprobación de stock.
        qty_by_book = {}
        book_by_id = {}
        for line in self.line_ids:
            if not line.book_id:
                continue
            book_id = line.book_id.id
            qty_by_book[book_id] = qty_by_book.get(book_id, 0) + line.quantity
            book_by_id[book_id] = line.book_id
        return qty_by_book, book_by_id

    def _check_stock_available(self):
        # Verifica que la tienda tenga stock suficiente antes de confirmar.
        # Nota importante sobre concurrencia:
        # - En entornos con varios usuarios simultáneos, leer la cantidad
        #   y luego restarla puede producir condiciones de carrera.
        # - Para producción con tráfico, considera usar bloqueo de fila
        #   (SELECT FOR UPDATE) o el módulo `stock` de Odoo que maneja
        #   reservas y movimientos de forma segura.
        stock_model = self.env['library.stock']
        for order in self:
            if not order.store_id:
                raise ValidationError('Selecciona una tienda antes de confirmar la venta.')
            qty_by_book, book_by_id = order._get_qty_by_book()
            for book_id, requested_qty in qty_by_book.items():
                book = book_by_id[book_id]
                stock_line = stock_model.search([
                    ('store_id', '=', order.store_id.id),
                    ('book_id', '=', book_id),
                ], limit=1)
                available = stock_line.quantity if stock_line else 0
                if requested_qty > available:
                    raise ValidationError(
                        'No hay stock suficiente para %s en %s. Disponible: %s.'
                        % (book.display_name, order.store_id.display_name, available)
                    )

    def _consume_stock(self):
        # Descuenta stock por tienda tras confirmar o finalizar una venta.
        # Aviso: aquí se realiza la resta directa sobre `quantity`.
        # En escenarios concurrentes esto puede permitir sobreventa si
        # dos transacciones leen el mismo valor antes de restarlo.
        # Si necesitas seguridad, hay que aplicar locking o usar `stock`.
        stock_model = self.env['library.stock']
        for order in self:
            if not order.store_id:
                raise ValidationError('Selecciona una tienda antes de confirmar la venta.')
            qty_by_book, book_by_id = order._get_qty_by_book()
            for book_id, requested_qty in qty_by_book.items():
                book = book_by_id[book_id]
                stock_line = stock_model.search([
                    ('store_id', '=', order.store_id.id),
                    ('book_id', '=', book_id),
                ], limit=1)
                available = stock_line.quantity if stock_line else 0
                if requested_qty > available:
                    raise ValidationError(
                        'No hay stock suficiente para %s en %s. Disponible: %s.'
                        % (book.display_name, order.store_id.display_name, available)
                    )
                # Resta directa del stock. Se podría reemplazar por
                # un método que cree movimientos y reservas si se requiere
                # trazabilidad o seguridad frente a concurrencia.
                stock_line.quantity -= requested_qty


