# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    library_order_id = fields.Many2one(
        'library.order',
        string='Pedido GestiLibros',
        readonly=True,
        copy=False,
    )

    def action_view_library_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedido GestiLibros',
            'res_model': 'library.order',
            'res_id': self.library_order_id.id,
            'view_mode': 'form',
        }
