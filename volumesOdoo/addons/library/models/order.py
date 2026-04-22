# -*- coding: utf-8 -*-
from odoo import models, fields, api




class LibraryOrder(models.Model):
    _name = 'library.order'
    _description = 'Venta'
    _order = 'date desc, id desc'

    name = fields.Char(string='Referencia', readonly=True, default='New')
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

    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.line_ids.mapped('price_subtotal'))


