from odoo import models, fields


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Autor'

    name = fields.Char(string='Nombre', required=True)
    nationality = fields.Char(string='Nacionalidad')
    date_of_birth = fields.Date(string='Fecha de nacimiento')
    book_ids = fields.Many2many(
        'library.book',
        'library_book_author_rel',
        'author_id',
        'book_id',
        string='Libros',
    )
