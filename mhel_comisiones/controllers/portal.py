# -*- coding: utf-8 -*-

import json

from datetime import time, datetime

import logging
_logger = logging.getLogger(__name__)

from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'guests_count' in counters:
            values['guests_count'] = len(partner.sudo().get_invitados())
        return values

    @http.route('/my/guests', type='http', auth="user", website=True, methods=['GET', 'POST'], csrf=False)
    def portal_my_guests(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        _logger.info('##############################')
        _logger.info('RUTA: /my/guests')
        _logger.info('##############################')
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

        _logger.info('##############################')
        _logger.info(values)
        _logger.info('##############################')
        
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
