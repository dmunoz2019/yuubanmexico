# -*- coding: utf-8 -*-
import re
from odoo.http import request
from odoo import http
import logging

_logging = logging.getLogger(__name__)

class MyController(http.Controller):
    @http.route('/contract_form', type='http', auth='public', methods=['GET'], website=True, cors='*')
    def contract_form(self, iddist=None):
        user = request.env['res.users'].sudo()
        country = request.env['res.country'].sudo().with_context(lang='es_ES').search([])
        bank = request.env['res.bank'].sudo().search([])
        # lets set the lang in es_ES in a variable
        if iddist:
            _logging.info(f'Buscando usuario con iddist {iddist}')
            user = user.search([('iddist', '=', int(iddist))])
            _logging.info(f'Usuario encontrado: {user}')
            if not user:
                return "Usuario no encontrado!"
        _logging.info(f'Banks: {bank}')
        return http.request.render('client_qr.portal_contract_form', {
            'user': user, 
            'countries': country,
            'banks': bank,
        })

    @http.route('/contract-submitted', type='http', auth='public', methods=['GET', 'POST'], website=True)
    def contract_submitted(self, **post):
        if 'identification_number' not in post:
            return self.handle_missing_identification_number(post)
        return self.handle_existing_identification_number(post)

    def handle_missing_identification_number(self, post):
        anfitrion = request.env['res.partner'].sudo().search([('is_head', '=', True)])
        if not anfitrion:
            return "No hay un distribuidor principal, por favor contacte a soporte"
        
        post['identification_number'] = anfitrion.iddist
        return self.create_partner(post, anfitrion)

    def handle_existing_identification_number(self, post):
        anfitrion = request.env['res.partner'].sudo().search([('iddist', '=', post['identification_number'])])
        return self.create_partner(post, anfitrion)

    def create_partner(self, post, anfitrion):
        partner_verify = request.env['res.partner'].sudo().search([('email', '=', post['email'])])
        if partner_verify:
            _logging.info(f'Usuario ya existe: {partner_verify}')
            return "Usuario ya existe, por favor espere a ser redirigido a la página anterior"
        if post.get('bank_id'):
            bank_id = int(post['bank_id'])
            bank = request.env['res.bank'].sudo().search([('id', '=', bank_id)])

        partner = request.env['res.partner'].sudo().create({
            'name': f"{post['first_name']} {post['last_name_father']} {post['last_name_mother']}",
            'street': post['address'],
            'city': post['city'],
            'zip': post['zip_code'],
            'phone': post['phone'],
            'email': post['email'],
            'function': 'Distribuidor',
            'vat': post['identification_number'],
            'birth_date': post['birth_date'],
            'city': post['city'],
            'state': post['state'],
            'country_id': int(post['country_id']),
            'rfc': post['rfc'],
            'anfitrion_id': int(anfitrion.id),

        })
        if post.get('bank_id') and post.get('acc_number') and post.get('clabe') and post.get('branch') and post.get('first_name') and post.get('last_name_father') and post.get('last_name_mother'):
            partner.write({
                'bank_ids': [(0, 0, {
                    'bank_id': post['bank_id'],
                    'acc_number': post['acc_number'],
                    'l10n_mx_edi_clabe': post['clabe'],
                    'branch': post['branch'],
                    'acc_holder_name': f"{post['first_name']} {post['last_name_father']} {post['last_name_mother']}",
                    'partner_id': partner.id,
                })],
            })


        portal_user = request.env['res.users'].sudo().create({
            'login': post['email'],
            'partner_id': partner.id,
            'company_id': request.env.company.id,
            'name': f"{post['first_name']} {post['last_name_father']} {post['last_name_mother']}",
            'active': True,
            'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],

        })

        _logging.info(f'Partner creado: {partner}')

        _logging.info(f'Usuario creado: {portal_user}')

        return request.redirect('/my')
