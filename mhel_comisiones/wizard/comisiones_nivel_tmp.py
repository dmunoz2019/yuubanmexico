# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ComisionesNivelTmp(models.TransientModel):
    _name = 'comisiones.nivel.tmp'
    _description = 'Calculo temporal de niveles'

    process_id = fields.Integer('ID Proceso')
    partner_id = fields.Integer('Cliente')
    partner_curr_id = fields.Integer('Cliente validado')
    nivel = fields.Integer('Nivel')
