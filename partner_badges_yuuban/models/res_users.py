from odoo import models, fields, api
from datetime import datetime, timedelta
import calendar
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    user_badge_ids = fields.One2many('user.badge', 'user_id', string='Badges de Ventas')
    top_badge_id = fields.Many2one('sale.badge', string='Insignia de Ventas más alta', compute='_compute_top_badge')
    top_badge_image = fields.Binary(string='Insignia de Ventas', related='top_badge_id.badge_image')

    def _compute_top_badge(self):
        for user in self:
            user.top_badge_id = user.user_badge_ids and user.user_badge_ids.sorted(key=lambda x: x.badge_id.level, reverse=True)[0].badge_id or False
