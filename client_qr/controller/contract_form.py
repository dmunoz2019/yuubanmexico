# -*- coding: utf-8 -*-
import re
from odoo.http import request
from odoo import http
import logging

_logging = logging.getLogger(__name__)

class MyController(http.Controller):
    @http.route('/contract_form', type='http', auth='public', methods=['GET'], website=True)
    def contract_form(self, iddist=None):
        user = request.env['res.users'].sudo()
        country = request.env['res.country'].sudo().with_context(lang='es_ES').search([])
        bank = request.env['res.bank'].sudo().search([])
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
            r = self.handle_missing_identification_number(post)
            return  http.request.render('client_qr.portal_contract_submitted', {
            'data': post,})
        r =  self.handle_existing_identification_number(post)
        return  http.request.render('client_qr.portal_contract_submitted', {
            'data': post,})

    def handle_missing_identification_number(self, post):
        anfitrion = request.env['res.partner'].sudo().search([('is_head', '=', True)])
        if not anfitrion:
            return "<h1>No hay un distribuidor principal, por favor contacte a soporte</h1>"
        
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
        bank_id = int(post['bank_id']) if post['bank_id'] else False
        bank = request.env['res.bank'].sudo().search([('id', '=', bank_id)]) if bank_id else False

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
        if bank:
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
        

    # @http.route('/contract-submitted', type='http', auth='public', methods=['GET','POST'], website=True)
    # def contract_submitted(self, **post):
    #     user = request.env['res.users'].sudo()
    #     # vamos a crear el usuario de los datos del formulario 

        
    #     return "Contrato enviado!"
    # @http.route('/contract-submitted', type='http', auth='public', methods=['GET', 'POST'], website=True)
    # def contract_submitted(self, **post):
    #     required_fields = ['identification_number', 'last_name_father', 'last_name_mother', 'first_name', 'city', 'state', 'birth_date', 'birth_place', 'address', 'zip_code', 'phone', 'email', 'rfc', 'bank_name', 'account_number', 'bank_branch', 'card_number', 'clabe', 'sponsor_last_name_father', 'sponsor_last_name_mother', 'sponsor_first_name']
    #     missing_fields = [field for field in required_fields if field not in post]
    #     if 'identification_number' not in post:
    #         anfitrion = request.env['res.partner'].sudo().search([('is_head', '=', True)])
    #         if not anfitrion:
    #             return "No hay un distribuidor principal, por favor contacte a soporte"
    #         else:
    #             post['identification_number'] = anfitrion.iddist
    #             partner_verify = request.env['res.partner'].sudo().search([('email', '=', post['email'])])

            
    #         partner_verify = request.env['res.partner'].sudo().search([('email', '=', post['email'])])
    #         if partner_verify:
    #             _logging.info(f'Usuario ya existe: {partner_verify}')
    #             # lets return a message to the uset wait to be redirected to the previous page
    #             return "Usuario ya existe, por favor espere a ser redirigido a la página anterior"
    #         partner = request.env['res.partner'].sudo().create({
    #             'name': f"{post['first_name']} {post['last_name_father']} {post['last_name_mother']}",
    #             'street': post['address'],
    #             'city': post['city'],
    #             'zip': post['zip_code'],
    #             'phone': post['phone'],
    #             'email': post['email'],
    #             'function': 'Distribuidor',
    #             'vat': post['identification_number'],
    #             'birth_date': post['birth_date'],
    #             'birth_place': post['birth_place'],
    #             'rfc': post['rfc'],
    #             'anfitrion_id': anfitrion.id,
    #         })

    #         _logging.info(f'Partner creado: {partner}')

    #         return "Contrato enviado con éxito!"
        
    #     else:       
    #         anfitrion = request.env['res.partner'].sudo().search([('iddist', '=', post['identification_number'])])
    #         partner_verify = request.env['res.partner'].sudo().search([('email', '=', post['email'])])
    #         if partner_verify:
    #             _logging.info(f'Usuario ya existe: {partner_verify}')
    #             # lets return a message to the uset wait to be redirected to the previous page
    #             return "Usuario ya existe, por favor espere a ser redirigido a la página anterior"
    #         partner = request.env['res.partner'].sudo().create({
    #             'name': f"{post['first_name']} {post['last_name_father']} {post['last_name_mother']}",
    #             'street': post['address'],
    #             'city': post['city'],
    #             'zip': post['zip_code'],
    #             'phone': post['phone'],
    #             'email': post['email'],
    #             'function': 'Distribuidor',
    #             'vat': post['identification_number'],
    #             'birth_date': post['birth_date'],
    #             'birth_place': post['birth_place'],
    #             'rfc': post['rfc'],
    #             'anfitrion_id': anfitrion.id,
    #         })

    #         _logging.info(f'Partner creado: {partner}')


    #         if partner:
    #             # Crear el registro del usuario en la base de datos
    #             user = request.env['res.users'].sudo().create({
    #                 'login': post['email'],
    #                 'partner_id': partner.id,
    #                 'company_id': request.env.company.id,
    #                 'company_type': 'person',
    #                 'name': f"{post['first_name']} {post['last_name_father']} {post['last_name_mother']}",
    #                 'active': True,
    #                 'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
    #             })

            # bank = request.env['res.partner.bank'].sudo().create({
            #     'acc_number': post['account_number'],
            #     'bank_name': post['bank_name'],
            #     'branch': post['bank_branch'],
            #     'clabe': post['clabe'],
            #     'partner_id': partner.id,
            # })

            # # Loguear el proceso
            # request.env['ir.logging'].sudo().create({
            #     'name': 'Contract Submission',
            #     'type': 'server',
            #     'dbname': request.session.db,
            #     'level': 'INFO',
            #     'message': f'Contrato enviado: {post}',
            #     'path': 'contract_submitted',
            #     'func': 'contract_submitted',
            #     'line': '22',
            # })

            # return "Contrato enviado con éxito!"

