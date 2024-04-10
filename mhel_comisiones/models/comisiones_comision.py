# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ComisionesComision(models.Model):
    _name = 'comisiones.comision'
    _description = 'Calculo de comisiones'

    date_start = fields.Date('Fecha corte inicial')
    date_end = fields.Date('Fecha corte final')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    partner_ori_id = fields.Many2one('res.partner', string='Cliente origen')
    sale_line_id = fields.Many2one('sale.order.line', string='Linea comisionable')
    amount_comision = fields.Float(string='Valor comisionable')
    por_comision = fields.Float(string='% Comision')
    val_comision = fields.Float(string='Valor Comision')
    state = fields.Selection([
            ('open','Por Pagar'),
            ('paid', 'Pagada'),]
        , string='Estado comision', index=True, readonly=True, default='open', copy=False)
    nivel = fields.Integer('Nivel')
    date_liquidacion = fields.Datetime('Fecha liquidacion')
    liquidador_id = fields.Many2one('res.users', string='Liquidado por')

    def calcular_comisiones(self, partner_id, sale_ids, periodo_id, comisiones_valor_meta, por_comision_nivel1, por_comision_nivel2, por_comision_nivel3, por_comision_nivel4, por_comision_nivel5):
        data = []
        sale_filtradas_ids = sale_ids.filtered(lambda x: x.partner_id == partner_id)
        total_ventas = sum(sale_filtradas_ids.mapped('val_comisionable'))
        if total_ventas >= comisiones_valor_meta:
            # Comisiones nivel 1
            nivel_alcanzado = 0
            nivel1_partner_ids = partner_id.invitado_ids
            for nivel1_partner_id in nivel1_partner_ids:
                sale_filtradas_nivel1_ids = sale_ids.filtered(lambda x: x.partner_id == nivel1_partner_id)
                total_ventas = sum(sale_filtradas_nivel1_ids.mapped('val_comisionable'))
                if total_ventas:
                    data.append({
                        'date_start': periodo_id.date_start,
                        'date_end': periodo_id.date_end,
                        'partner_id': partner_id.id,
                        'partner_ori_id': nivel1_partner_id.id,
                        'amount_comision': total_ventas,
                        'por_comision': por_comision_nivel1,
                        'val_comision': total_ventas * por_comision_nivel1 / 100,
                        'nivel': 1,
                    })
                    if total_ventas >= comisiones_valor_meta:
                        nivel_alcanzado += 1
            # Comisiones nivel 2
            if nivel_alcanzado >= 2:
                nivel2_partner_ids = self.env['res.partner']
                for nivel1_partner_id in nivel1_partner_ids:
                    nivel2_partner_ids |= nivel1_partner_id.invitado_ids
                for nivel2_partner_id in nivel2_partner_ids:
                    sale_filtradas_nivel2_ids = sale_ids.filtered(lambda x: x.partner_id == nivel2_partner_id)
                    total_ventas = sum(sale_filtradas_nivel2_ids.mapped('val_comisionable'))
                    if total_ventas:
                        data.append({
                            'date_start': periodo_id.date_start,
                            'date_end': periodo_id.date_end,
                            'partner_id': partner_id.id,
                            'partner_ori_id': nivel2_partner_id.id,
                            'amount_comision': total_ventas,
                            'por_comision': por_comision_nivel2,
                            'val_comision': total_ventas * por_comision_nivel2 / 100,
                            'nivel': 2,
                        })
            # Comisiones nivel 3
            if nivel_alcanzado >= 3:
                nivel3_partner_ids = self.env['res.partner']
                for nivel2_partner_id in nivel2_partner_ids:
                    nivel3_partner_ids |= nivel2_partner_id.invitado_ids
                for nivel3_partner_id in nivel3_partner_ids:
                    sale_filtradas_nivel3_ids = sale_ids.filtered(lambda x: x.partner_id == nivel3_partner_id)
                    total_ventas = sum(sale_filtradas_nivel3_ids.mapped('val_comisionable'))
                    if total_ventas:
                        data.append({
                            'date_start': periodo_id.date_start,
                            'date_end': periodo_id.date_end,
                            'partner_id': partner_id.id,
                            'partner_ori_id': nivel3_partner_id.id,
                            'amount_comision': total_ventas,
                            'por_comision': por_comision_nivel3,
                            'val_comision': total_ventas * por_comision_nivel3 / 100,
                            'nivel': 3,
                        })
            # Comisiones nivel 4
            if nivel_alcanzado >= 4:
                nivel4_partner_ids = self.env['res.partner']
                for nivel3_partner_id in nivel3_partner_ids:
                    nivel4_partner_ids |= nivel3_partner_id.invitado_ids
                for nivel4_partner_id in nivel4_partner_ids:
                    sale_filtradas_nivel4_ids = sale_ids.filtered(lambda x: x.partner_id == nivel4_partner_id)
                    total_ventas = sum(sale_filtradas_nivel4_ids.mapped('val_comisionable'))
                    if total_ventas:
                        data.append({
                            'date_start': periodo_id.date_start,
                            'date_end': periodo_id.date_end,
                            'partner_id': partner_id.id,
                            'partner_ori_id': nivel4_partner_id.id,
                            'amount_comision': total_ventas,
                            'por_comision': por_comision_nivel4,
                            'val_comision': total_ventas * por_comision_nivel4 / 100,
                            'nivel': 4,
                        })
            # Comisiones nivel 5
            if nivel_alcanzado >= 5:
                nivel5_partner_ids = self.env['res.partner']
                for nivel4_partner_id in nivel4_partner_ids:
                    nivel5_partner_ids |= nivel4_partner_id.invitado_ids
                for nivel5_partner_id in nivel5_partner_ids:
                    sale_filtradas_nivel5_ids = sale_ids.filtered(lambda x: x.partner_id == nivel5_partner_id)
                    total_ventas = sum(sale_filtradas_nivel5_ids.mapped('val_comisionable'))
                    if total_ventas:
                        data.append({
                            'date_start': periodo_id.date_start,
                            'date_end': periodo_id.date_end,
                            'partner_id': partner_id.id,
                            'partner_ori_id': nivel5_partner_id.id,
                            'amount_comision': total_ventas,
                            'por_comision': por_comision_nivel5,
                            'val_comision': total_ventas * por_comision_nivel5 / 100,
                            'nivel': 5,
                        })
        return data
