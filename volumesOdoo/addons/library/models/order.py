# -*- coding: utf-8 -*-
from odoo import models, fields




class LibraryOrder(models.Model):
    _name = 'library.order'
    _description = 'Pedido'
    _order = 'date desc, id desc'

    name = fields.Char(string='Referencia', readonly=True, default='New')
    client_id = fields.Many2one('res.partner', string='Cliente', required=True)
    date = fields.Datetime(string='Fecha', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('done', 'Hecho'),
        ('cancel', 'Cancelado')
    ], default='draft')
    line_ids = fields.One2many('library.order.line', 'order_id', string='Líneas de pedido', copy=True)
    currency_id = fields.Many2one('res.currency', string='Moneda')
    amount_total = fields.Monetary(string='Total', readonly=True)


