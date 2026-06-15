# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryOrder(models.Model):
    _name = 'library.order'
    _description = 'Venta'
    _order = 'date desc, id desc'

    name = fields.Char(string='Referencia', readonly=True, default='New', copy=False)
    store_id = fields.Many2one('library.store', string='Tienda', required=True)
    client_id = fields.Many2one('res.partner', string='Cliente', required=True)
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
    # Referencia a la factura generada al confirmar
    invoice_id = fields.Many2one('account.move', string='Factura', readonly=True, copy=False)

    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.line_ids.mapped('price_subtotal'))

    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise ValidationError('No puedes confirmar una venta sin lineas.')
            order._check_stock_available()
            order._consume_stock()
            # Asignar número de secuencia al confirmar (igual que hace sale.order)
            if order.name == 'New':
                order.name = self.env['ir.sequence'].sudo().next_by_code('library.order') or 'New'
            # Crear factura automáticamente en el módulo de Contabilidad
            invoice = order._create_invoice()
            order.invoice_id = invoice.id
            order.state = 'confirmed'

    def action_done(self):
        for order in self:
            if order.state == 'draft':
                if not order.line_ids:
                    raise ValidationError('No puedes confirmar una venta sin lineas.')
                order._check_stock_available()
                order._consume_stock()
                if order.name == 'New':
                    order.name = self.env['ir.sequence'].sudo().next_by_code('library.order') or 'New'
            # Garantiza la factura y la CONFIRMA (contabiliza) automáticamente al
            # cerrar la venta: el usuario no tiene que confirmarla a mano.
            # sudo() para que un Vendedor pueda cerrar la venta sin permisos de Contabilidad.
            if not order.invoice_id:
                order.invoice_id = order._create_invoice().id
            if order.invoice_id.sudo().state == 'draft':
                order.invoice_id.sudo().action_post()
            order.state = 'done'

    def action_cancel(self):
        for order in self:
            order.state = 'cancel'

    def action_reset_draft(self):
        for order in self:
            order.state = 'draft'

    def action_view_invoice(self):
        # Abre la factura asociada directamente desde el pedido.
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factura',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
        }

    def _create_invoice(self):
        # Genera una factura de cliente (out_invoice) a partir de las líneas
        # del pedido. Aprovecha la integración con account.move de Odoo.
        # Las líneas se mapean a account.move.line con tipo 'product'.
        self.ensure_one()
        move_lines = []
        for line in self.line_ids:
            move_lines.append((0, 0, {
                'name': line.book_id.display_name,
                'quantity': line.quantity,
                'price_unit': line.unit_price,
                # account_id es opcional: si la empresa tiene cuenta de ingresos
                # por defecto, Odoo la asigna automáticamente.
            }))
        # sudo(): el Vendedor no tiene permisos de Contabilidad, pero la venta
        # debe poder generar su factura igualmente.
        invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'partner_id': self.client_id.id,
            'invoice_date': fields.Date.today(),
            'currency_id': self.currency_id.id,
            'invoice_line_ids': move_lines,
            'ref': self.name if self.name != 'New' else False,
            # Enlace inverso al pedido (herencia account.move)
            'library_order_id': self.id,
        })
        return invoice

    def _get_qty_by_book(self):
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
                stock_line.quantity -= requested_qty
