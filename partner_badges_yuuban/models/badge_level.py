# lets create a model to set the level for the badge

from odoo import models, fields

class BadgeLevel(models.Model):
    _name = 'badge.level'
    _description = 'Badge Level'

    name = fields.Char(string='Name', required=True)
    level = fields.Integer(string='Level', required=True)
    description = fields.Text(string='Description', required=True)