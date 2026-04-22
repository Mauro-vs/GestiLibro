# -*- coding: utf-8 -*-
from odoo import models, fields


class LibraryPublisher(models.Model):
    _name = 'library.publisher'
    _description = 'Editorial'

    name = fields.Char(string='Nombre', required=True)
    country = fields.Char(string='País')
    website = fields.Char(string='Sitio web')
    book_ids = fields.One2many('library.book', 'publisher_id', string='Libros')
