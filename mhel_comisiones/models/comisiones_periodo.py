# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class ComisionesPeriodo(models.Model):
    _name = 'comisiones.periodo'
    _description = 'Periodo para el calculo de comisiones por cliente'

    name = fields.Char(string='Periodo')
    amount_meta = fields.Monetary(string='Valor meta periodo')
    date_start = fields.Date(string='Fecha inicio')
    date_end = fields.Date(string='Fecha fin')
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
    )

    @api.model
    def create(self, vals):
        self.search([('active', '=', True)]).write({'active': False})
        return super(ComisionesPeriodo, self).create(vals)

    def write(self, vals):
        if 'active' in vals and vals['active']:
            comisiones_periodo_ids = self.search([('active', '=', True)])
            if comisiones_periodo_ids:
                raise UserError('Solo puede tener un periodo activo para la liquidación de comisiones')
        return super(ComisionesPeriodo, self).write(vals)
