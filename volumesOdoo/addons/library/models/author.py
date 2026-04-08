from odoo import models, fields


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Autor'

    name = fields.Char(string='Nombre', required=True)
    nationality = fields.Char(string='Nacionalidad')
    date_of_birth = fields.Date(string='Fecha de nacimiento')
