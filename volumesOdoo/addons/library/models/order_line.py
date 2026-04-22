# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LibraryOrderLine(models.Model):
    _name = 'library.order.line'
    _description = 'Línea de venta'

    _sql_constraints = [
        ('library_order_line_positive_quantity', 'CHECK(quantity > 0)', 'La cantidad debe ser mayor que cero.')
    ]

    order_id = fields.Many2one('library.order', string='Venta', required=True, ondelete='cascade')
    book_id = fields.Many2one('library.book', string='Libro', required=True)
    quantity = fields.Integer(string='Cantidad', default=1, required=True)
    unit_price = fields.Monetary(string='Precio unitario', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id', store=True, readonly=True)
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal', store=True)

    @api.onchange('book_id')
    def _onchange_book_id(self):
        for line in self:
            if line.book_id:
                line.unit_price = line.book_id.price_sale

    @api.depends('quantity', 'unit_price')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.unit_price
