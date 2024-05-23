from odoo import models, fields, api
from datetime import datetime, timedelta
import calendar
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    user_badge_ids = fields.One2many('user.badge', 'user_id', string='Badges de Ventas')
    top_badge_id = fields.Many2one('sale.badge', string='Insignia de Ventas más alta', compute='_compute_top_badge')
    top_badge_image = fields.Binary(string='Imagen de la Insignia de Ventas más alta', related='top_badge_id.badge_image')

    def _compute_top_badge(self):
        for user in self:
            user.top_badge_id = user.user_badge_ids and user.user_badge_ids.sorted(key=lambda x: x.badge_id.level, reverse=True)[0].badge_id or False

    def _evaluate_sales(self):
        today = fields.Date.today()
        _logger.info('Evaluando ventas para el día: %s', today)
        for user in self:
            badges = self._get_all_badges()
            max_existing_level = self._get_max_existing_level(user)
            new_badge, period_start, period_end, total_sales = self._get_new_badge(user, badges, today, max_existing_level)
            if new_badge:
                self._assign_badge(user, new_badge, period_start, period_end, total_sales)

    def _get_all_badges(self):
        badges = self.env['sale.badge'].search([], order='level')
        _logger.info('Insignias obtenidas: %s', badges)
        return badges

    def _get_max_existing_level(self, user):
        existing_badges = self.env['user.badge'].search([
            ('user_id', '=', user.id)
        ])
        max_level = max(existing_badges.mapped('badge_id.level'), default=0)
        _logger.info('Nivel máximo de insignia existente para el usuario %s: %d', user.id, max_level)
        return max_level

    def _get_new_badge(self, user, badges, today, max_existing_level):
        new_badge = None
        period_start = None
        period_end = None
        total_sales = 0

        for badge in badges:
            period_start, period_end = self._calculate_period(today, badge.period_length)
            total_sales = self._calculate_total_sales(user, period_start, period_end)

            _logger.info('Evaluando insignia %s: nivel %d, meta de ventas %.2f', badge.name, badge.level, badge.sales_target)
            _logger.info('Ventas totales para el usuario %s en el periodo del %s al %s: %.2f', user.id, period_start, period_end, total_sales)

            if total_sales >= badge.sales_target and badge.level > max_existing_level:
                new_badge = badge
                _logger.info('Nueva insignia seleccionada: %s', new_badge.name)
            else:
                break

        return new_badge, period_start, period_end, total_sales

    def _calculate_period(self, today, period_length):
        start_month = today.month - (today.month - 1) % period_length
        start_year = today.year

        if start_month > today.month:
            start_year -= 1

        period_start = datetime(start_year, start_month, 1)
        end_month = start_month + period_length - 1

        end_year = start_year
        if end_month > 12:
            end_year += 1
            end_month -= 12

        last_day_of_end_month = calendar.monthrange(end_year, end_month)[1]
        period_end = datetime(end_year, end_month, last_day_of_end_month)

        _logger.info('Período calculado: inicio %s, fin %s', period_start, period_end)
        return period_start, period_end

    def _calculate_total_sales(self, user, period_start, period_end):
        total_sales = sum(self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('partner_id', '=', user.partner_id.id),
            ('invoice_date', '>=', period_start),
            ('invoice_date', '<=', period_end),
        ]).mapped('amount_total'))

        _logger.info('Ventas totales calculadas para el usuario %s en el periodo del %s al %s: %.2f', user.id, period_start, period_end, total_sales)
        return total_sales

    def _assign_badge(self, user, new_badge, period_start, period_end, total_sales):
        self.env['user.badge'].create({
            'user_id': user.id,
            'badge_id': new_badge.id,
            'period_start': period_start,
            'period_end': period_end,
            'sales_volume': total_sales,
        })
        _logger.info('Asignada insignia %s al usuario %s por ventas de %.2f en el periodo del %s al %s', new_badge.name, user.id, total_sales, period_start, period_end)

    @api.model
    def _cron_evaluate_sales(self):
        self.search([])._evaluate_sales()