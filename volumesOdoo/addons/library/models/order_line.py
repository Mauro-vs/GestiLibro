# -*- coding: utf-8 -*-
from odoo import models, fields


class LibraryOrderLine(models.Model):
    _name = 'library.order.line'
    _description = 'Línea de pedido'

    order_id = fields.Many2one('library.order', string='Pedido', required=True, ondelete='cascade')
    book_id = fields.Many2one('library.book', string='Libro', required=True)
    quantity = fields.Integer(string='Cantidad', default=1)
    unit_price = fields.Monetary(string='Precio unitario', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id', store=True, readonly=True)
    price_subtotal = fields.Monetary(string='Subtotal')
