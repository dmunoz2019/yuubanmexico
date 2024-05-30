# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


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
    
    def obtener_partners_nivel(self, partner_id, nivel):
        partners_nivel_actual = partner_id.invitado_ids
        for _ in range(1, nivel):
            partners_nivel_siguiente = self.env['res.partner']
            for partner in partners_nivel_actual:
                partners_nivel_siguiente |= partner.invitado_ids
            partners_nivel_actual = partners_nivel_siguiente
        return partners_nivel_actual

    def calcular_comisiones_nivel(self, partner_id, sale_ids, periodo_id, porcentaje, nivel):
        data = []
        nivel_partner_ids = self.obtener_partners_nivel(partner_id, nivel)
        count = 0

        for nivel_partner_id in nivel_partner_ids:
            sale_filtradas_nivel_ids = sale_ids.filtered(lambda x: x.partner_id == nivel_partner_id)
            total_ventas = sum(sale_filtradas_nivel_ids.mapped('val_comisionable'))
            if total_ventas:
                count += 1
                data.append({
                    'date_start': periodo_id.date_start,
                    'date_end': periodo_id.date_end,
                    'partner_id': partner_id.id,
                    'partner_ori_id': nivel_partner_id.id,
                    'amount_comision': total_ventas,
                    'por_comision': porcentaje,
                    'val_comision': total_ventas * porcentaje / 100,
                    'nivel': nivel,
                })
        return data, count

    def calcular_comisiones(self, partner_id, sale_ids, periodo_id, comisiones_valor_meta, por_comision_nivel1, por_comision_nivel2, por_comision_nivel3, por_comision_nivel4, por_comision_nivel5):
        data = []
        sale_filtradas_ids = sale_ids.filtered(lambda x: x.partner_id == partner_id)
        total_ventas = sum(sale_filtradas_ids.mapped('val_comisionable'))
        nivel1_count = 0
        nivel2_count = 0
        nivel3_count = 0
        nivel4_count = 0
        if total_ventas >= comisiones_valor_meta:
            nivel1_data, nivel1_count = self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel1, 1)
            data += nivel1_data
            if nivel1_count > 0:
                nivel2_data, nivel2_count = self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel2, 2)
                data += nivel2_data
            if nivel2_count > 0:
                nivel3_data, nivel3_count = self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel3, 3)
                data += nivel3_data
            if nivel3_count > 0:
                nivel4_data, nivel4_count = self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel4, 4)
                data += nivel4_data
            if nivel4_count > 0:
                nivel5_data, nivel5_count = self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel5, 5)
                data += nivel5_data
        return data


    
    # def obtener_partners_nivel(self, partner_id, nivel):
    #     partners_nivel_actual = partner_id.invitado_ids
    #     for _ in range(1, nivel):
    #         partners_nivel_siguiente = self.env['res.partner']
    #         for partner in partners_nivel_actual:
    #             partners_nivel_siguiente |= partner.invitado_ids
    #         partners_nivel_actual = partners_nivel_siguiente
    #     return partners_nivel_actual

    # def calcular_comisiones_nivel(self, partner_id, sale_ids, periodo_id, porcentaje, nivel):
    #     data = []
    #     nivel_partner_ids = self.obtener_partners_nivel(partner_id, nivel)

    #     for nivel_partner_id in nivel_partner_ids:
    #         sale_filtradas_nivel_ids = sale_ids.filtered(lambda x: x.partner_id == nivel_partner_id)
    #         total_ventas = sum(sale_filtradas_nivel_ids.mapped('val_comisionable'))
    #         if total_ventas:
    #             data.append({
    #                 'date_start': periodo_id.date_start,
    #                 'date_end': periodo_id.date_end,
    #                 'partner_id': partner_id.id,
    #                 'partner_ori_id': nivel_partner_id.id,
    #                 'amount_comision': total_ventas,
    #                 'por_comision': porcentaje,
    #                 'val_comision': total_ventas * porcentaje / 100,
    #                 'nivel': nivel,
    #             })
    #     return data

    # def calcular_comisiones(self, partner_id, sale_ids, periodo_id, comisiones_valor_meta, por_comision_nivel1, por_comision_nivel2, por_comision_nivel3, por_comision_nivel4, por_comision_nivel5):
    #     data = []
    #     sale_filtradas_ids = sale_ids.filtered(lambda x: x.partner_id == partner_id)
    #     total_ventas = sum(sale_filtradas_ids.mapped('val_comisionable'))
    #     if total_ventas >= comisiones_valor_meta:
    #         # Comisiones por nivel
    #         data += self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel1, 1)
    #         if any(rec['nivel'] == 1 for rec in data):
    #             data += self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel2, 2)
    #         if any(rec['nivel'] == 2 for rec in data):
    #             data += self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel3, 3)
    #         if any(rec['nivel'] == 3 for rec in data):
    #             data += self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel4, 4)
    #         if any(rec['nivel'] == 4 for rec in data):
    #             data += self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel5, 5)
    #     return data

    # def obtener_partners_nivel(self, partner_id, nivel):
    #     if nivel == 1:
    #         return partner_id.invitado_ids
    #     else:
    #         partners_nivel_actual = partner_id.invitado_ids
    #         for _ in range(1, nivel):
    #             partners_nivel_siguiente = self.env['res.partner']
    #             for partner in partners_nivel_actual:
    #                 partners_nivel_siguiente |= partner.invitado_ids
    #             partners_nivel_actual = partners_nivel_siguiente
    #         return partners_nivel_actual

    # def calcular_comisiones_nivel(self, partner_id, sale_ids, periodo_id, porcentaje, nivel):
    #     data = []
    #     nivel_partner_ids = self.obtener_partners_nivel(partner_id, nivel)

    #     for nivel_partner_id in nivel_partner_ids:
    #         sale_filtradas_nivel_ids = sale_ids.filtered(lambda x: x.partner_id == nivel_partner_id)
    #         total_ventas = sum(sale_filtradas_nivel_ids.mapped('val_comisionable'))
    #         if total_ventas:
    #             data.append({
    #                 'date_start': periodo_id.date_start,
    #                 'date_end': periodo_id.date_end,
    #                 'partner_id': partner_id.id,
    #                 'partner_ori_id': nivel_partner_id.id,
    #                 'amount_comision': total_ventas,
    #                 'por_comision': porcentaje,
    #                 'val_comision': total_ventas * porcentaje / 100,
    #                 'nivel': nivel,
    #             })
    #     return data


    # def calcular_comisiones(self, partner_id, sale_ids, periodo_id, comisiones_valor_meta, por_comision_nivel1, por_comision_nivel2, por_comision_nivel3, por_comision_nivel4, por_comision_nivel5):
    #     data = []
    #     sale_filtradas_ids = sale_ids.filtered(lambda x: x.partner_id == partner_id)
    #     total_ventas = sum(sale_filtradas_ids.mapped('val_comisionable'))
    #     if total_ventas >= comisiones_valor_meta:
    #         # Comisiones por nivel
    #         data += self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel1, 1)
    #         if any(rec['nivel'] == 1 for rec in data):
    #             data += self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel2, 2)
    #         if any(rec['nivel'] == 2 for rec in data):
    #             data += self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel3, 3)
    #         if any(rec['nivel'] == 3 for rec in data):
    #             data += self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel4, 4)
    #         if any(rec['nivel'] == 4 for rec in data):
    #             data += self.calcular_comisiones_nivel(partner_id, sale_ids, periodo_id, por_comision_nivel5, 5)
    #     return data




    # def calcular_comisiones(self, partner_id, sale_ids, periodo_id, comisiones_valor_meta, por_comision_nivel1, por_comision_nivel2, por_comision_nivel3, por_comision_nivel4, por_comision_nivel5):
    #     data = []
    #     sale_filtradas_ids = sale_ids.filtered(lambda x: x.partner_id == partner_id)
    #     total_ventas = sum(sale_filtradas_ids.mapped('val_comisionable'))
    #     if total_ventas >= comisiones_valor_meta:
    #         # Comisiones nivel 1
    #         nivel_alcanzado = 0
    #         nivel1_partner_ids = partner_id.invitado_ids
    #         for nivel1_partner_id in nivel1_partner_ids:
    #             sale_filtradas_nivel1_ids = sale_ids.filtered(lambda x: x.partner_id == nivel1_partner_id)
    #             total_ventas = sum(sale_filtradas_nivel1_ids.mapped('val_comisionable'))
    #             if total_ventas:
    #                 data.append({
    #                     'date_start': periodo_id.date_start,
    #                     'date_end': periodo_id.date_end,
    #                     'partner_id': partner_id.id,
    #                     'partner_ori_id': nivel1_partner_id.id,
    #                     'amount_comision': total_ventas,
    #                     'por_comision': por_comision_nivel1,
    #                     'val_comision': total_ventas * por_comision_nivel1 / 100,
    #                     'nivel': 1,
    #                 })
    #                 if total_ventas >= comisiones_valor_meta:
    #                     nivel_alcanzado += 1
    #         # Comisiones nivel 2
    #         if nivel_alcanzado >= 2:
    #             nivel2_partner_ids = self.env['res.partner']
    #             for nivel1_partner_id in nivel1_partner_ids:
    #                 nivel2_partner_ids |= nivel1_partner_id.invitado_ids
    #             for nivel2_partner_id in nivel2_partner_ids:
    #                 sale_filtradas_nivel2_ids = sale_ids.filtered(lambda x: x.partner_id == nivel2_partner_id)
    #                 total_ventas = sum(sale_filtradas_nivel2_ids.mapped('val_comisionable'))
    #                 if total_ventas:
    #                     data.append({
    #                         'date_start': periodo_id.date_start,
    #                         'date_end': periodo_id.date_end,
    #                         'partner_id': partner_id.id,
    #                         'partner_ori_id': nivel2_partner_id.id,
    #                         'amount_comision': total_ventas,
    #                         'por_comision': por_comision_nivel2,
    #                         'val_comision': total_ventas * por_comision_nivel2 / 100,
    #                         'nivel': 2,
    #                     })
    #         # Comisiones nivel 3
    #         if nivel_alcanzado >= 3:
    #             nivel3_partner_ids = self.env['res.partner']
    #             for nivel2_partner_id in nivel2_partner_ids:
    #                 nivel3_partner_ids |= nivel2_partner_id.invitado_ids
    #             for nivel3_partner_id in nivel3_partner_ids:
    #                 sale_filtradas_nivel3_ids = sale_ids.filtered(lambda x: x.partner_id == nivel3_partner_id)
    #                 total_ventas = sum(sale_filtradas_nivel3_ids.mapped('val_comisionable'))
    #                 if total_ventas:
    #                     data.append({
    #                         'date_start': periodo_id.date_start,
    #                         'date_end': periodo_id.date_end,
    #                         'partner_id': partner_id.id,
    #                         'partner_ori_id': nivel3_partner_id.id,
    #                         'amount_comision': total_ventas,
    #                         'por_comision': por_comision_nivel3,
    #                         'val_comision': total_ventas * por_comision_nivel3 / 100,
    #                         'nivel': 3,
    #                     })
    #         # Comisiones nivel 4
    #         if nivel_alcanzado >= 4:
    #             nivel4_partner_ids = self.env['res.partner']
    #             for nivel3_partner_id in nivel3_partner_ids:
    #                 nivel4_partner_ids |= nivel3_partner_id.invitado_ids
    #             for nivel4_partner_id in nivel4_partner_ids:
    #                 sale_filtradas_nivel4_ids = sale_ids.filtered(lambda x: x.partner_id == nivel4_partner_id)
    #                 total_ventas = sum(sale_filtradas_nivel4_ids.mapped('val_comisionable'))
    #                 if total_ventas:
    #                     data.append({
    #                         'date_start': periodo_id.date_start,
    #                         'date_end': periodo_id.date_end,
    #                         'partner_id': partner_id.id,
    #                         'partner_ori_id': nivel4_partner_id.id,
    #                         'amount_comision': total_ventas,
    #                         'por_comision': por_comision_nivel4,
    #                         'val_comision': total_ventas * por_comision_nivel4 / 100,
    #                         'nivel': 4,
    #                     })
    #         # Comisiones nivel 5
    #         if nivel_alcanzado >= 5:
    #             nivel5_partner_ids = self.env['res.partner']
    #             for nivel4_partner_id in nivel4_partner_ids:
    #                 nivel5_partner_ids |= nivel4_partner_id.invitado_ids
    #             for nivel5_partner_id in nivel5_partner_ids:
    #                 sale_filtradas_nivel5_ids = sale_ids.filtered(lambda x: x.partner_id == nivel5_partner_id)
    #                 total_ventas = sum(sale_filtradas_nivel5_ids.mapped('val_comisionable'))
    #                 if total_ventas:
    #                     data.append({
    #                         'date_start': periodo_id.date_start,
    #                         'date_end': periodo_id.date_end,
    #                         'partner_id': partner_id.id,
    #                         'partner_ori_id': nivel5_partner_id.id,
    #                         'amount_comision': total_ventas,
    #                         'por_comision': por_comision_nivel5,
    #                         'val_comision': total_ventas * por_comision_nivel5 / 100,
    #                         'nivel': 5,
    #                     })
    #     return data
