from odoo import models, fields

class UserBadge(models.Model):
    _name = 'user.badge'
    _description = 'Badge Asignado a Usuario'

    user_id = fields.Many2one('res.users', string='Usuario', required=True)
    badge_id = fields.Many2one('sale.badge', string='Badge', required=True)
    sales_volume = fields.Float(string='Volumen de Ventas', required=True)
    period_start = fields.Date(string='Inicio del Período', required=True)
    period_end = fields.Date(string='Fin del Período', required=True)
