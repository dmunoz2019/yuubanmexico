# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ComisionesLiquidacionWizard(models.TransientModel):
    _name = 'comisiones.liquidacion.wizard'
    _description = 'Liquidar comisiones por anfitrión'

    partner_ids = fields.Many2many('res.partner', 'comisiones_liq_report_partner_rel', 'partner_id',
                                   'comision_report_id', string='Terceros', copy=False)

    def action_liquidar_comisiones(self):

        if not self.partner_ids:
            comisiones = self.env['comisiones.comision'].search([('state', '=', 'open')])
        else:
            comisiones = self.env['comisiones.comision'].search(
                [('state', '=', 'open'), ('partner_id', 'in', self.partner_ids.ids)])

        for comision in comisiones:
            comision.state = 'paid'
            user = self.env['res.users'].browse(self._context['uid'])
            comision.liquidador_id = user
            comision.date_liquidacion = fields.Date.today()

        return {'type': 'ir.actions.act_window_close'}

    def action_exit(self):
        return {'type': 'ir.actions.act_window_close'}