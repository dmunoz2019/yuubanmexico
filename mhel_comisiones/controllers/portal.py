# -*- coding: utf-8 -*-

import json

from datetime import time, datetime

import logging
_logger = logging.getLogger(__name__)

from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from dateutil.relativedelta import relativedelta


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'guests_count' in counters:
            values['guests_count'] = len(partner.sudo().get_invitados())
        return values

    def generar_reporte(self):
        _logger.info('#############Generando reporte#################')
        data = []
        consolidado = {}
        tz_offset = int(request.env.user.tz_offset.replace('-', '').replace('0', ''))
        periodo_id = request.env['comisiones.periodo'].sudo().with_context(active_test=False).search([], order='id desc', limit=1)
        _logger.info(f'############# Generando reporte para periodo '+str(periodo_id)+' #################')
        date_start = datetime.combine(periodo_id.date_start, time(0, 0, 0)) + relativedelta(hours=tz_offset)
        date_end = datetime.combine(periodo_id.date_end, time(0, 0, 0)) + relativedelta(days=1, hours=tz_offset)
        sale_ids = request.env['sale.order'].sudo().search([
            ('state', '=', 'sale'),
            ('date_order', '>=', date_start),
            ('date_order', '<=', date_end),
        ])
        partner_id = request.env.user.partner_id
        subordinados_ids = partner_id.sudo().invitado_ids
        partner_ids = sale_ids.mapped('partner_id').filtered(lambda x: x.id in subordinados_ids.ids)        
        comisiones_valor_meta = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.valor.meta', 3500))
        por_comision_nivel1 = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.primer.nivel', 35))
        por_comision_nivel2 = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.segundo.nivel', 15))
        por_comision_nivel3 = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.tercer.nivel', 3))
        por_comision_nivel4 = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.cuarto.nivel', 2))
        por_comision_nivel5 = float(request.env['ir.config_parameter'].sudo().get_param('comisiones.quinto.nivel', 5))
        for partner_id in partner_ids.sorted(key=lambda x: x.name):
            comision = request.env['comisiones.comision'].calcular_comisiones(
                partner_id,
                sale_ids,
                # Lets use the last period using env
                periodo_id,
                comisiones_valor_meta,
                por_comision_nivel1,
                por_comision_nivel2,
                por_comision_nivel3,
                por_comision_nivel4,
                por_comision_nivel5,
            )
            if comision:
                data += comision
        if data:
             for record in data:
                 if record['partner_id'] not in consolidado:
                     consolidado[record['partner_id']] = {
                         'nivel1': 0,
                         'nivel2': 0,
                         'nivel3': 0,
                         'nivel4': 0,
                         'nivel5': 0,
                     }
                 if record['nivel'] == 1:
                     consolidado[record['partner_id']]['nivel1'] += record['val_comision']
                 elif record['nivel'] == 2:
                     consolidado[record['partner_id']]['nivel2'] += record['val_comision']
                 elif record['nivel'] == 3:
                     consolidado[record['partner_id']]['nivel3'] += record['val_comision']
                 elif record['nivel'] == 4:
                     consolidado[record['partner_id']]['nivel4'] += record['val_comision']
                 elif record['nivel'] == 5:
                     consolidado[record['partner_id']]['nivel5'] += record['val_comision']
        datos_tabla = []
        for dato in consolidado:
            datos_tabla.append({
                'nivel1': consolidado[dato]['nivel1'],
                'nivel2': consolidado[dato]['nivel2'],
                'nivel3': consolidado[dato]['nivel3'],
                'nivel4': consolidado[dato]['nivel4'],
                'nivel5': consolidado[dato]['nivel5'],
                'total': consolidado[dato]['nivel1'] + consolidado[dato]['nivel2'] + consolidado[dato]['nivel3'] + consolidado[dato]['nivel4'] + consolidado[dato]['nivel5'],
            })
        sumas = {
        'nivel1': 0,
        'nivel2': 0,
        'nivel3': 0,
        'nivel4': 0,
        'nivel5': 0,
        'total': 0
        }

        for dato in datos_tabla:
            sumas['nivel1'] += dato['nivel1']
            sumas['nivel2'] += dato['nivel2']
            sumas['nivel3'] += dato['nivel3']
            sumas['nivel4'] += dato['nivel4']
            sumas['nivel5'] += dato['nivel5']
            sumas['total'] += dato['total']
            

        _logger.info('################Termino el calculo##############')
        # _logger.info(date_start)
        # _logger.info('##############################')
        # _logger.info(date_end)
        # _logger.info('##############################')
        # _logger.info(sale_ids)
        # _logger.info('#############/partner ids#################')
        # _logger.info(partner_ids)
        # _logger.info('##############################')
        # _logger.info(periodo_id)
        # _logger.info('##############################')
        # _logger.info(comisiones_valor_meta)
        # _logger.info('##############################')
        # _logger.info(por_comision_nivel1)
        # _logger.info('##############################')
        # _logger.info(por_comision_nivel2)
        # _logger.info('##############################')
        # _logger.info(por_comision_nivel3)
        # _logger.info('##############################')
        # _logger.info(por_comision_nivel4)
        # _logger.info('##############################')
        # _logger.info(por_comision_nivel5)
        # _logger.info('##############################')
        # _logger.info(request.env.user.partner_id.name)
        # _logger.info('##############################')
        # _logger.info(sumas)
        # _logger.info('##############################')
        return sumas

    @http.route('/my/guests', type='http', auth="user", website=True, methods=['GET', 'POST'], csrf=False)
    def portal_my_guests(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        _logger.info('##############################')
        _logger.info('RUTA: /my/guests')
        _logger.info('##############################')
        sumas = self.generar_reporte()
        values = {}
        try:
            values = self._prepare_portal_layout_values()
            partner = request.env.user.partner_id
            invitados_ids = partner.sudo().get_invitados()
            periodo_id = kw.get('periodo_id', False)
            comisiones = {}
            comisiones_periodo_ids = request.env['comisiones.periodo'].sudo().with_context(active_test=False).search([]).sorted('active', reverse=True)
            for comisiones_periodo_id in comisiones_periodo_ids:
                if not periodo_id:
                    periodo_id = comisiones_periodo_id.id
                comisiones[str(comisiones_periodo_id.id)] = '{0}: {1:02d}-{2:02d}-{3} / {4:02d}-{5:02d}-{6}'.format(
                    comisiones_periodo_id.name,
                    comisiones_periodo_id.date_start.day,
                    comisiones_periodo_id.date_start.month,
                    comisiones_periodo_id.date_start.year,
                    comisiones_periodo_id.date_end.day,
                    comisiones_periodo_id.date_end.month,
                    comisiones_periodo_id.date_end.year,
                )
            subordinados = self._get_subordinados(partner.id, str(periodo_id))
            comisiones_periodo_id = request.env['comisiones.periodo'].sudo().browse(int(periodo_id))
            fch_inicio = datetime.combine(comisiones_periodo_id.date_start, time(0, 0, 0))
            fch_fin = datetime.combine(comisiones_periodo_id.date_end, time(0, 0, 0))
            sale_ids = request.env['sale.order'].sudo().search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', fch_inicio),
                ('date_order', '<=', fch_fin),
            ])

            values.update({
                'route_guests': partner.name + ' / ',
                'page_name': 'guest',
                'default_url': '/my/guests',
                'searchbar_sortings': False,
                'sortby': sortby,
                'guest': partner,
                'invitados_ids': invitados_ids,
                'comisiones': comisiones,
                'subordinados': subordinados,
                'periodo_id': str(periodo_id),
                'sales': [{'name': x.name, 'date': x.date_order.strftime('%d/%m/%Y %H:%M:%S'), 'amount_total': x.amount_total, 'val_comisionable': x.val_comisionable}  for x in sale_ids],
                'total_ventas': sum(sale_ids.mapped('amount_total')),
                'total_comisionable': sum(sale_ids.mapped('val_comisionable')),
            })
        except Exception as e:
            _logger.info("#### ERROR FUNCION portal_my_guests ####")
            _logger.info(e)
        suma =[]
        values.update(sumas)

        _logger.info('###############Valores###############')
        _logger.info(values)
        _logger.info('##############################')
        _logger.info('##############Sumas################')
        _logger.info(sumas)
        _logger.info('##############################')

        # lets insert sumas into values

        
        return request.render("mhel_comisiones.portal_my_guests", values)

    def _get_subordinados(self, partner_id, periodo_id):
        
        subordinado = {}
        sales = []
        
        try:
            partner_id = request.env['res.partner'].sudo().browse(partner_id)
            subordinados_ids = partner_id.sudo().invitado_ids
            for sub in subordinados_ids:
                comisiones_periodo_id = request.env['comisiones.periodo'].sudo().browse(int(periodo_id))
                fch_inicio = datetime.combine(comisiones_periodo_id.date_start, time(0, 0, 0))
                fch_fin = datetime.combine(comisiones_periodo_id.date_end, time(0, 0, 0))
                sale_ids = request.env['sale.order'].sudo().search([
                    ('partner_id', '=', sub.id),
                    ('state', 'in', ['sale', 'done']),
                    ('date_order', '>=', fch_inicio),
                    ('date_order', '<=', fch_fin),
                ])
                subordinado[str(sub.id)] = {
                    'name': sub.name,
                    'importe': sum(sale_ids.mapped('val_comisionable')),
                }

            # Tablas
            comisiones_periodo_id = request.env['comisiones.periodo'].sudo().browse(int(periodo_id))
            fch_inicio = datetime.combine(comisiones_periodo_id.date_start, time(0, 0, 0))
            fch_fin = datetime.combine(comisiones_periodo_id.date_end, time(0, 0, 0))

            sales = [{'name': x.name, 'date': x.date_order.strftime('%d/%m/%Y %H:%M:%S'), 'amount_total': x.amount_total, 'val_comisionable': x.val_comisionable}  for x in request.env['sale.order'].sudo().search([
                ('partner_id', '=', partner_id.id),
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', fch_inicio),
                ('date_order', '<=', fch_fin),
            ])]
        except Exception as e:
            print("#### ERROR FUNCION _get_subordinados ####")
            print(e)

        return {
            "subordinado": subordinado,
            "sales": sales
        }

    @http.route('/my/guests/<int:partner_id>/<int:periodo_id>', type='http', auth="user", website=True, methods=['GET', 'POST'], csrf=False)
    def portal_my_guests_detail(self, partner_id, periodo_id, **kw):
        return json.dumps(self._get_subordinados(partner_id, periodo_id))
