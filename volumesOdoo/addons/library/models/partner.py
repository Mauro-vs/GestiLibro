# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_library_customer = fields.Boolean(string='Cliente GestiLibros', default=False)
    library_customer_code = fields.Char(string='Codigo cliente')
    favorite_genre = fields.Selection(
        [
            ('novel', 'Novela'),
            ('history', 'Historia'),
            ('science', 'Ciencia'),
            ('fantasy', 'Fantasia'),
            ('other', 'Otro'),
        ],
        string='Genero favorito',
    )
    loyalty_points = fields.Integer(string='Puntos de fidelidad', default=0)
    sale_count = fields.Integer(string='Numero de ventas', compute='_compute_sale_count')

    @api.depends('is_library_customer')
    def _compute_sale_count(self):
        # Conteo sencillo de ventas por cliente para mostrar contexto comercial.
        order_model = self.env['library.order']
        for partner in self:
            partner.sale_count = order_model.search_count([('client_id', '=', partner.id)])