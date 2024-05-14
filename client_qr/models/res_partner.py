from odoo import api, fields, models
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    birth_date = fields.Date(string='Fecha de nacimiento')
    birth_place = fields.Char( string='Lugar de nacimiento')
    country_id = fields.Many2one('res.country', string='País')
    rfc = fields.Char(string='RFC')
    is_head = fields.Boolean(string='Es cabeza')
    city = fields.Char(string='Ciudad')
    state = fields.Char(string='Estado')

    # we are gouin to use a boolean field to set the head of all the partners, it can be only one, if we create or update a partner with this field set to true, we are going to validate that there is no other partner with this field set to true
    @api.constrains('is_head')
    def _check_is_head(self):
        for partner in self:
            if partner.is_head:
                head_partner = self.search([('is_head', '=', True)])
                if head_partner and head_partner.id != partner.id:
                    raise ValidationError(f'Ya existe un distribuidor principal, solo puede haber uno. Distribuidor principal actual: {head_partner.name}')