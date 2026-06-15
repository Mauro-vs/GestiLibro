# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryPublisher(models.Model):
    _name = 'library.publisher'
    _description = 'Editorial'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    # País usando res.country en lugar de texto libre.
    country_id = fields.Many2one('res.country', string='País')
    website = fields.Char(string='Sitio web')
    phone = fields.Char(string='Teléfono')
    book_ids = fields.One2many('library.book', 'publisher_id', string='Libros')

    @api.constrains('name')
    def _check_unique_name(self):
        # Impide dar de alta dos editoriales con el mismo nombre.
        for publisher in self:
            normalized = (publisher.name or '').strip().lower()
            duplicate = self.search([
                ('id', '!=', publisher.id),
            ]).filtered(lambda p: (p.name or '').strip().lower() == normalized)
            if duplicate:
                raise ValidationError('Ya existe una editorial con ese nombre: %s.' % publisher.name)
