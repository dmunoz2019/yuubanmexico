# -*- coding: utf-8 -*-

from datetime import time, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ComisionesWizard(models.TransientModel):
    _name = 'comisiones.wizard'
    _description = 'Calcular comisiones por anfitrión'

    date_start = fields.Date('Fecha inicial')
    date_end = fields.Date('Fecha final')
    partner_ids = fields.Many2many('res.partner', 'comisiones_report_partner_rel', 'partner_id', 'comision_report_id', string='Terceros', copy=False)

    def action_calcular_niveles(self):
        # NUEVA FUNCION
        data = []
        periodo_id = self.env['comisiones.periodo'].search([], limit=1)
        if not periodo_id:
            raise ValidationError('No hay un periodo activo para liquidar comisiones')
        self.env['comisiones.comision'].search([
            ('date_start', '=', periodo_id.date_start),
            ('date_end', '=', periodo_id.date_end),
            ('partner_id', 'in', self.partner_ids.ids)
        ]).unlink()
        tz_offset = int(self.env.user.tz_offset.replace('-', '').replace('0', ''))
        date_start = datetime.combine(periodo_id.date_start, time(0, 0, 0)) + relativedelta(hours=tz_offset)
        date_end = datetime.combine(periodo_id.date_end, time(0, 0, 0)) + relativedelta(days=1, hours=tz_offset)
        sale_ids = self.env['sale.order'].search([
            ('state', '=', 'sale'),
            ('date_order', '>=', date_start),
            ('date_order', '<=', date_end)
        ])
        comisiones_valor_meta = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.valor.meta', 3500))
        por_comision_nivel1 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.primer.nivel', 35))
        por_comision_nivel2 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.segundo.nivel', 15))
        por_comision_nivel3 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.tercer.nivel', 3))
        por_comision_nivel4 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.cuarto.nivel', 2))
        por_comision_nivel5 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.quinto.nivel', 5))
        for partner_id in self.partner_ids:
            comision = self.env['comisiones.comision'].calcular_comisiones(partner_id, sale_ids, periodo_id, comisiones_valor_meta, por_comision_nivel1, por_comision_nivel2, por_comision_nivel3, por_comision_nivel4, por_comision_nivel5)
            if comision:
                data += comision
        if data:
            self.env['comisiones.comision'].create(data)

    def action_exit(self):
        return {'type': 'ir.actions.act_window_close'}
