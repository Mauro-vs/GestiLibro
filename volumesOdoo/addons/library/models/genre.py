# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryGenre(models.Model):
    _name = 'library.genre'
    _description = 'Género literario'
    _order = 'name'

    # Modelo propio para que la empresa gestione los géneros (alta/baja)
    # y que libros y clientes compartan exactamente la misma lista.
    _sql_constraints = [
        ('library_genre_name_uniq', 'unique(name)', 'Ya existe un género con ese nombre.'),
    ]

    name = fields.Char(string='Género', required=True)
    description = fields.Text(string='Descripción')
    book_ids = fields.One2many('library.book', 'genre_id', string='Libros')
    book_count = fields.Integer(string='Nº de libros', compute='_compute_book_count')

    @api.depends('book_ids')
    def _compute_book_count(self):
        for genre in self:
            genre.book_count = len(genre.book_ids)

    @api.constrains('name')
    def _check_unique_name(self):
        # Evita duplicados aunque difieran en mayúsculas/espacios.
        for genre in self:
            normalized = (genre.name or '').strip().lower()
            duplicate = self.search([
                ('id', '!=', genre.id),
            ]).filtered(lambda g: (g.name or '').strip().lower() == normalized)
            if duplicate:
                raise ValidationError('Ya existe un género con ese nombre: %s.' % genre.name)
