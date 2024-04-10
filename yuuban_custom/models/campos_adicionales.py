# -*- coding:utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.osv import osv, expression
import logging
_logger = logging.getLogger(__name__)
import re


class Clientes(models.Model):    
    _inherit = "res.partner"
    
    # agrega campos a res.partner como informacion adicional de contactos


    iddist = fields.Char("Id de Cliente",  default=lambda self: _('New'), readonly=False)
    
    @api.model
    def create(self, vals):
        if vals.get('iddist', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['iddist'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('Cliente') or _('New')
            else:
                vals['iddist'] = self.env['ir.sequence'].next_by_code('Cliente') or _('New')

        result = super(Clientes, self).create(vals)
        return result
    
    
    
    _sql_constraints = [
        ('iddist_unique', 'unique(iddist)',
         'El Id de Distribuidor debe ser único')]


