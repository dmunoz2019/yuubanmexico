# models/sale_badge.py
from odoo import models, fields

class SaleBadge(models.Model):
    _name = 'sale.badge'
    _description = 'Badge de Ventas'

    name = fields.Char(string='Nombre del Badge', required=True)
    sales_target = fields.Float(string='Meta de Ventas', required=True)
    level = fields.Integer(string='Nivel', required=True)
    period_start = fields.Date(string='Inicio del Periodo', required=True)
    period_end = fields.Date(string='Fin del Periodo', required=True)
    period_length = fields.Integer(string='Longitud del Período (meses)', required=True, default=3)
