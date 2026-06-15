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
    library_customer_code = fields.Char(string='Código cliente', copy=False, readonly=True)
    # Género favorito apuntando al mismo modelo que los libros (library.genre):
    # así el cliente dispone exactamente de los mismos géneros que el catálogo.
    favorite_genre_id = fields.Many2one('library.genre', string='Género favorito')
    loyalty_points = fields.Integer(string='Puntos de fidelidad', default=0)
    # Desde la ficha del cliente son sus "compras" (las ventas de la tienda).
    purchase_count = fields.Integer(string='Compras', compute='_compute_purchase_count')
    library_order_ids = fields.One2many('library.order', 'client_id', string='Compras')

    @api.depends('library_order_ids', 'library_order_ids.state')
    def _compute_purchase_count(self):
        for partner in self:
            partner.purchase_count = len(
                partner.library_order_ids.filtered(lambda o: o.state in ('confirmed', 'done'))
            )

    def _next_customer_code(self):
        return self.env['ir.sequence'].next_by_code('library.customer') or False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_library_customer') and not vals.get('library_customer_code'):
                vals['library_customer_code'] = self._next_customer_code()
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        # Al marcar un contacto como cliente, se le asigna código automáticamente.
        if vals.get('is_library_customer'):
            for partner in self.filtered(lambda p: p.is_library_customer and not p.library_customer_code):
                partner.library_customer_code = partner._next_customer_code()
        return res

    def action_view_library_orders(self):
        # Abre la lista de compras del cliente (usado por el stat button).
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Compras',
            'res_model': 'library.order',
            'view_mode': 'list,form',
            'domain': [('client_id', '=', self.id)],
            'context': {'default_client_id': self.id},
        }

    @api.constrains('is_library_customer', 'library_customer_code')
    def _check_library_customer_code(self):
        for partner in self:
            if partner.is_library_customer and not partner.library_customer_code:
                raise ValidationError('El código de cliente es obligatorio para clientes GestiLibros.')
