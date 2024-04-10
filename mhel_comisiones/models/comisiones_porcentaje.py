# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ComisionesPorcentaje(models.Model):
    _name = 'comisiones.porcentaje'
    _description = 'Porcentajes de comisiones'

    subnivel = fields.Integer('Subnivel')
    por_comision = fields.Float('Porcentaje Comision')
