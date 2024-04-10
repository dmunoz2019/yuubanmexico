# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartnerExt(models.Model):
    _inherit = 'res.partner'

    def _get_comisiones2(self, partner_cr_id, subnivel, date_start=None, date_end=None, meta=0.0, process_id=0):
        resultado = []
        if not self.invitado_ids:
            val_com = 0
            orders = self.env['sale.order'].search(
                [('partner_id', '=', self.id), ('date_order', '>=', date_start), ('date_order', '<=', date_end),
                 ('state', '=', 'sale')]).ids
            lines = self.env['sale.order.line'].search([('order_id', 'in', orders)])
            lines_ids = []

            for line in lines:
                val_com = val_com + line.price_subtotal
                lines_ids.append(line.id)

            esActivo = False

            if val_com >= meta:
                esActivo = True

            if esActivo:
                for line in lines:

                    if line.is_comisionable:

                        porcentaje = self.env['comisiones.porcentaje'].search([('subnivel', '=', subnivel)], limit=1)

                        vals = {
                            'date_start': date_start,
                            'date_end': date_end,
                            'partner_id': partner_cr_id,
                            'sale_line_id': line.id,
                            'amount_comision': line.price_subtotal,
                            'por_comision': porcentaje.por_comision,
                            'val_comision': (line.price_subtotal * porcentaje.por_comision) / 100,
                            'nivel': subnivel,
                            'partner_ori_id': self.id,
                        }

                        if partner_cr_id != self.id:
                            resultado.append(vals)
        else:

            subnivel = subnivel + 1

            for inv in self.invitado_ids:

                val_com = 0

                orders = self.env['sale.order'].search(
                    [('partner_id', '=', inv.id), ('date_order', '>=', date_start), ('date_order', '<=', date_end),
                     ('state', '=', 'sale')]).ids
                lines = self.env['sale.order.line'].search([('order_id', 'in', orders)])

                for line in lines:
                    val_com = val_com + line.price_subtotal

                esActivo = False

                if val_com >= meta:
                    esActivo = True

                res = inv._get_comisiones2(partner_cr_id, subnivel, date_start, date_end, meta, process_id)
                for element in res:
                    if element:
                        resultado.append(element)

                if esActivo and inv.invitado_ids:

                    for line in lines:

                        if line.is_comisionable:

                            porcentaje = self.env['comisiones.porcentaje'].search([('subnivel', '=', subnivel)],
                                                                                  limit=1)

                            vals = {
                                'date_start': date_start,
                                'date_end': date_end,
                                'partner_id': partner_cr_id,
                                'sale_line_id': line.id,
                                'amount_comision': line.price_subtotal,
                                'por_comision': porcentaje.por_comision,
                                'val_comision': (line.price_subtotal * porcentaje.por_comision) / 100,
                                'nivel': subnivel,
                                'partner_ori_id': inv.id,
                            }

                            if partner_cr_id != inv.id:
                                resultado.append(vals)
        return resultado