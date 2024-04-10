# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'guests_count' in counters:
            values['guests_count'] = len(partner.sudo().get_invitados())
        return values

    def _get_child_node(self, partner, ids_guest=[], parent_id = 0):
        if partner.invitado_ids:
            for x in partner.invitado_ids:
                ids_guest += self._get_child_node(x, ids_guest, parent_id)
            if partner.id != parent_id:
                ids_guest.append(partner.id)
        else:
            if partner.id != parent_id:
                ids_guest.append(partner.id)
        
        return ids_guest

    def _prepare_guest_domain(self, partner):

        base = []
        ids_guest = self._get_child_node(partner, base, partner.id)

        return [
            ('id', 'in', ids_guest)
        ]

    @http.route(['/my/guests', '/my/guests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_guests(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        _logger = logging.getLogger(__name__)
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        invitados_ids = partner.sudo().get_invitados()

        #sales2 = request.env['sale.order'].sudo().search([('id', '=', 1995)])

        #for x1 in invitados_ids:

        # for x1 in invitados_ids:
        #     cantidad = 0
        #     sales = http.request.env['sale.order'].sudo().search([('partner_id', '=', x1.id)])
        #     for x2 in sales:
        #         cantidad = cantidad + x2.amount_total
        #     _logger.error(cantidad)
        # buscando sales order

        sales_ids = http.request.env['sale.order'].sudo().search([('state', '=', 'sale')])

        values.update({
            'date': date_begin,
            'partnersppal': partner,
            'page_name': 'guest',
            'default_url': '/my/guests',
            'searchbar_sortings': False,
            'sortby': sortby,
            'guest': partner,
            'route_guests': partner.name + ' / ',
            'invitados_ids': invitados_ids,
            'sales_id': sales_ids,
        })
        return request.render("mhel_comisiones.portal_my_guests", values)
