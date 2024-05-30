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
        bank = None
        partner_verify = request.env['res.partner'].sudo().search([('email', '=', post['email'])])
        bank_info = " "
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
        if post.get('bank_id') and post.get('acc_number'):
            _logging.info(f'Creando cuenta bancaria')

            bank_account = request.env['res.partner.bank'].sudo().create({
                'acc_number': post['acc_number'],
                'partner_id': partner.id,
                'bank_id': bank.id,
            })
            bank_info = f"""
            <p class="data-field"><strong>Banco:</strong> {bank.name}</p>
            <p class="data-field"><strong>Número de Cuenta:</strong> {post['acc_number']}</p>
            """
            _logging.info(f'Cuenta bancaria creada: {bank_account}')


        # portal_user = request.env['res.users'].sudo().create({
        #     'login': post['email'],
        #     'partner_id': partner.id,
        #     'company_id': request.env.company.id,
        #     'name': f"{post['first_name']} {post['last_name_father']} {post['last_name_mother']}",
        #     'active': True,
        #     'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],

        # })
        # lets create a lead in crm for this partner with the use with the email gaby_corporativo@yuubanmexico.com.mx 
        # as responsible

        user_id = request.env['res.users'].sudo().search([('login', '=','nanci_corporativo@yuubanmexico.com.mx')])

        lead = request.env['crm.lead'].sudo().create(
            {
                'partner_id': partner.id,
                'user_id': user_id.id,
                'name': f"{post['first_name']} {post['last_name_father']} {post['last_name_mother']} de {post['state']}",
                'email_from':  post['email'],
                'phone' : post['phone'],
                'stage_id': 2,
                'description': f"""

                <style>
                    body {{
                        font-family: Arial, sans-serif;
                    }}
                    .profile {{
                        margin: 20px;
                        padding: 20px;
                        border: 1px solid #000;
                    }}
                    .profile h1 {{
                        text-align: center;
                        font-size: 24px;
                    }}
                    .profile p {{
                        margin: 10px 0;
                        font-size: 14px;
                    }}
                    .profile .section-title {{
                        font-weight: bold;
                        font-size: 18px;
                        margin-top: 20px;
                    }}
                    .profile .data-field {{
                        margin: 5px 0;
                    }}
                </style>
                       <div class="profile">
                    <h1>Ficha de Usuario</h1>
                    <p class="data-field"><strong>Nombre:</strong> {post.get('first_name', 'N/A')} {post.get('last_name_father', '')} {post.get('last_name_mother', '')}</p>
                    <p class="data-field"><strong>Dirección:</strong> {post.get('address', 'N/A')}</p>
                    <p class="data-field"><strong>Ciudad:</strong> {post.get('city', 'N/A')}</p>
                    <p class="data-field"><strong>Estado:</strong> {post.get('state', 'N/A')}</p>
                    <p class="data-field"><strong>Código Postal:</strong> {post.get('zip_code', 'N/A')}</p>
                    <p class="data-field"><strong>Teléfono:</strong> {post.get('phone', 'N/A')}</p>
                    <p class="data-field"><strong>Email:</strong> {post.get('email', 'N/A')}</p>
                    <p class="data-field"><strong>Número de Identificación:</strong> {post.get('identification_number', 'N/A')}</p>
                    <p class="data-field"><strong>Fecha de Nacimiento:</strong> {post.get('birth_date', 'N/A')}</p>
                    <p class="data-field"><strong>RFC:</strong> {post.get('rfc', 'N/A')}</p>
                    <p class="data-field"><strong>País:</strong> {request.env['res.country'].sudo().browse(int(post.get('country_id', 0))).name if post.get('country_id') else 'N/A'}</p>
                    <p class="data-field"><strong>Anfitrión ID:</strong> {anfitrion.id}</p>
                     {bank_info}
                </div>
                """
            }
        )
        user_nanci = request.env['res.users'].sudo().search([('login', '=', 'nanci_corporativo@yuubanmexico.com.mx')], limit=1)
        if not user_nanci:
            raise ValueError("Usuario 'Nanci Mosqueda' no encontrado.")

        # Creamos una nota en el lead
        note_content = f"""
        <p>@{user_nanci.name}</p>
        <p>Se ha creado una nueva ficha de usuario con los siguientes datos:</p>
        <ul>
            <li><strong>Nombre:</strong> {post.get('first_name', 'N/A')} {post.get('last_name_father', '')} {post.get('last_name_mother', '')}</li>
            <li><strong>Dirección:</strong> {post.get('address', 'N/A')}</li>
            <li><strong>Ciudad:</strong> {post.get('city', 'N/A')}</li>
            <li><strong>Estado:</strong> {post.get('state', 'N/A')}</li>
            <li><strong>Código Postal:</strong> {post.get('zip_code', 'N/A')}</li>
            <li><strong>Teléfono:</strong> {post.get('phone', 'N/A')}</li>
            <li><strong>Email:</strong> {post.get('email', 'N/A')}</li>
            <li><strong>Número de Identificación:</strong> {post.get('identification_number', 'N/A')}</li>
            <li><strong>Fecha de Nacimiento:</strong> {post.get('birth_date', 'N/A')}</li>
            <li><strong>RFC:</strong> {post.get('rfc', 'N/A')}</li>
            <li><strong>País:</strong> {request.env['res.country'].sudo().browse(int(post.get('country_id', 0))).name if post.get('country_id') else 'N/A'}</li>
            <li><strong>Anfitrión ID:</strong> {anfitrion.id}</li>
            {bank_info}
        </ul>
        """
            # Creación de la nota
        lead.message_post(
            body=note_content,
            subject="Nueva ficha de usuario creada",
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            partner_ids=[user_nanci.partner_id.id],
            email_from=user_nanci.email
        )
        
        user_gaby = request.env['res.users'].sudo().search([('login', '=', 'gaby_corporativo@yuubanmexico.com.mx')], limit=1)

        lead.message_subscribe(partner_ids=[user_gaby.partner_id.id])



       

        return request.redirect('/')
