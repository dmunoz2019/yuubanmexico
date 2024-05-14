# lets extend bank model to add a branch field

from odoo import models, fields

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    branch = fields.Char(string='Branch', required=True)
    clabe = fields.Char(string='CLABE', required=True)