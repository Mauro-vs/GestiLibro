# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Reglas de integridad para clientes del sistema.
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
    # Preferencias del cliente para personalizacion basica.
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
    # Indicadores comerciales visibles en la ficha del cliente.
    sale_count = fields.Integer(string='Numero de ventas', compute='_compute_sale_count')
    library_order_ids = fields.One2many('library.order', 'client_id', string='Ventas')

    @api.depends('library_order_ids', 'library_order_ids.state')
    def _compute_sale_count(self):
        # Cuenta ventas confirmadas o hechas para evitar inflar el indicador.
        # Aviso de rendimiento: para clientes con cientos/miles de pedidos,
        # esta estrategia carga las órdenes en memoria. Alternativa rápida:
        # usar `read_group` para que la BD haga la agregación.
        for partner in self:
            partner.sale_count = len(
                partner.library_order_ids.filtered(lambda order: order.state in ('confirmed', 'done'))
            )

    @api.constrains('is_library_customer', 'library_customer_code')
    def _check_library_customer_code(self):
        # Si es cliente, el codigo es obligatorio para identificarlo.
        for partner in self:
            if partner.is_library_customer and not partner.library_customer_code:
                raise ValidationError('El codigo de cliente es obligatorio para clientes GestiLibros.')