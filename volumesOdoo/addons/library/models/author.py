# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Autor'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    # Nacionalidad usando res.country en lugar de texto libre.
    country_id = fields.Many2one('res.country', string='Nacionalidad')
    date_of_birth = fields.Date(string='Fecha de nacimiento')
    biography = fields.Text(string='Biografía breve')
    image = fields.Image(string='Foto', max_width=512, max_height=512)
    book_ids = fields.Many2many(
        'library.book',
        'library_book_author_rel',
        'author_id',
        'book_id',
        string='Libros',
    )

    @api.constrains('name')
    def _check_unique_name(self):
        # Impide dar de alta dos autores con el mismo nombre.
        for author in self:
            normalized = (author.name or '').strip().lower()
            duplicate = self.search([
                ('id', '!=', author.id),
            ]).filtered(lambda a: (a.name or '').strip().lower() == normalized)
            if duplicate:
                raise ValidationError('Ya existe un autor con ese nombre: %s.' % author.name)
