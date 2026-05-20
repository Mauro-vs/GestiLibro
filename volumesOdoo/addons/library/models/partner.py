# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [
        (
            'library_customer_code_uniq',
            'unique(library_customer_code)',
            'El codigo de cliente debe ser unico.',
        ),
        (
            'library_customer_loyalty_nonneg',
            'CHECK(loyalty_points >= 0)',
            'Los puntos de fidelidad deben ser positivos.',
        ),
    ]

    is_library_customer = fields.Boolean(string='Cliente GestiLibros', default=False)
    library_customer_code = fields.Char(string='Codigo cliente')
    favorite_genre = fields.Selection(
        [
            ('novel', 'Novela'),
            ('history', 'Historia'),
            ('science', 'Ciencia'),
            ('fantasy', 'Fantasía'),
            ('other', 'Otro'),
        ],
        string='Género favorito',
    )
    loyalty_points = fields.Integer(string='Puntos de fidelidad', default=0)
    sale_count = fields.Integer(string='Ventas', compute='_compute_sale_count')
    library_order_ids = fields.One2many('library.order', 'client_id', string='Ventas')

    @api.depends('library_order_ids', 'library_order_ids.state')
    def _compute_sale_count(self):
        for partner in self:
            partner.sale_count = len(
                partner.library_order_ids.filtered(lambda o: o.state in ('confirmed', 'done'))
            )

    def action_view_library_orders(self):
        # Abre la lista de ventas filtrada por este cliente.
        # Usado por el stat_button de la ficha de cliente.
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ventas',
            'res_model': 'library.order',
            'view_mode': 'list,form',
            'domain': [('client_id', '=', self.id)],
            'context': {'default_client_id': self.id},
        }

    @api.constrains('is_library_customer', 'library_customer_code')
    def _check_library_customer_code(self):
        for partner in self:
            if partner.is_library_customer and not partner.library_customer_code:
                raise ValidationError('El codigo de cliente es obligatorio para clientes GestiLibros.')
