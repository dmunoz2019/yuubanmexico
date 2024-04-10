# -*- coding: utf-8 -*-

from datetime import time, datetime
from dateutil.relativedelta import relativedelta

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalComisiones(CustomerPortal):

    @http.route('/my/comisiones', type='http', auth="user", website=True, csrf=False)
    def portal_my_comisiones(self):
        # NUEVA FUNCION
        values = {}
        periodo_id = request.env['comisiones.periodo'].sudo().search([
            ('active', '=', True)
        ], limit=1)
        if not periodo_id:
            values = {'error': 'No se encontró periodo activo'}

        tz_offset = int(request.env.user.tz_offset.replace('-', '').replace('0', ''))
        date_start = datetime.combine(periodo_id.date_start, time(0, 0, 0)) + relativedelta(hours=tz_offset)
        date_end = datetime.combine(periodo_id.date_end, time(0, 0, 0)) + relativedelta(days=1, hours=tz_offset)
        sale_ids = request.env['sale.order'].sudo().search([
            ('state', '=', 'sale'),
            ('date_order', '>=', date_start),
            ('date_order', '=', date_end)
        ])
        comisiones_valor_meta = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.valor.meta', 3500))
        por_comision_nivel1 = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.primer.nivel', 35))
        por_comision_nivel2 = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.segundo.nivel', 15))
        por_comision_nivel3 = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.tercer.nivel', 3))
        por_comision_nivel4 = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.cuarto.nivel', 2))
        por_comision_nivel5 = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.quinto.nivel', 5))

        comision = request.env['comisiones.comision'].sudo().calcular_comisiones(
            request.env.user.partner_id,
            sale_ids,
            periodo_id,
            comisiones_valor_meta,
            por_comision_nivel1,
            por_comision_nivel2,
            por_comision_nivel3,
            por_comision_nivel4,
            por_comision_nivel5,
        )

        for element in comision:
            if element['nivel'] == 1:
                if 'total_nivel1_comisionable' in values:
                    values['total_nivel1_comisionable'] += element['amount_comision']
                    values['total_nivel1_comision'] += element['val_comision']
                else:
                    values['total_nivel1_comisionable'] = element['amount_comision']
                    values['total_nivel1_comision'] = element['val_comision']
            if element['nivel'] == 2:
                if 'total_nivel2_comisionable' in values:
                    values['total_nivel2_comisionable'] += element['amount_comision']
                    values['total_nivel2_comision'] += element['val_comision']
                else:
                    values['total_nivel2_comisionable'] = element['amount_comision']
                    values['total_nivel2_comision'] = element['val_comision']
            if element['nivel'] == 3:
                if 'total_nivel3_comisionable' in values:
                    values['total_nivel3_comisionable'] += element['amount_comision']
                    values['total_nivel3_comision'] += element['val_comision']
                else:
                    values['total_nivel3_comisionable'] = element['amount_comision']
                    values['total_nivel3_comision'] = element['val_comision']
            if element['nivel'] == 4:
                if 'total_nivel4_comisionable' in values:
                    values['total_nivel4_comisionable'] += element['amount_comision']
                    values['total_nivel4_comision'] += element['val_comision']
                else:
                    values['total_nivel4_comisionable'] = element['amount_comision']
                    values['total_nivel4_comision'] = element['val_comision']
            if element['nivel'] == 5:
                if 'total_nivel5_comisionable' in values:
                    values['total_nivel5_comisionable'] += element['amount_comision']
                    values['total_nivel5_comision'] += element['val_comision']
                else:
                    values['total_nivel5_comisionable'] = element['amount_comision']
                    values['total_nivel5_comision'] = element['val_comision']
        return request.render("comisiones_portal.comisiones_template", values)
