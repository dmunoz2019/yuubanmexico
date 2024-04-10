# -*- coding: utf-8 -*-

import ast
import logging

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class ResPartnerExt(models.Model):
    _inherit = 'res.partner'

    anfitrion_id = fields.Many2one('res.partner', string='Anfitrion')
    invitado_ids = fields.One2many('res.partner', 'anfitrion_id', string='Invitados del cliente')
    num_guests = fields.Char(string='Numero de invitados', store=False, readonly=True, compute='_compute_num_guests')
    nivel = fields.Char(string='Nivel', readonly=True)
    activos_directos = fields.Integer(string='Activos directos', readonly=True)
    inactivos_directos = fields.Integer(string='Inactivos directos', readonly=True)
    cumplimiento = fields.Float(string='% Cumplimiento', store=False, readonly=True, compute='_compute_amount_period')
    valor_periodo = fields.Float(string='Valor periodo actual', store=False, readonly=True, compute='_compute_amount_period')
    comisiones_por_pagar = fields.Float(string='Comisiones por pagar', store=False, readonly=True, compute='_compute_comisiones_por_pagar')

    def _get_asociados(self):
        return self.invitado_ids
    
    def _get_nivel(self, date_start, date_end, meta=0.0, process_id = 0):
        self.activos_directos = 0
        self.inactivos_directos = 0
        self.nivel = 0
        if not self.invitado_ids:
            self.nivel = 0
            val_com = 0
            orders = self.env['sale.order'].search([('partner_id', '=', self.id), ('date_order', '>=', date_start), ('date_order', '<=', date_end), ('state', '=', 'sale')]).ids
            lines = self.env['sale.order.line'].search([('order_id', 'in', orders)])
                
            for line in lines:
                val_com = val_com + line.price_subtotal

            esActivo = False

            if val_com >= meta:
                esActivo = True
                

            if esActivo:
                vals = {
                    'process_id': process_id,
                    'partner_id': self.anfitrion_id.id,
                    'partner_curr_id': self.id,
                    'nivel': 0,
                }

                com = self.env['comisiones.nivel.tmp'].create(vals)

        else:
            for inv in self.invitado_ids:

                val_com = 0

                orders = self.env['sale.order'].search([('partner_id', '=', inv.id), ('date_order', '>=', date_start), ('date_order', '<=', date_end), ('state', '=', 'sale')]).ids
                lines = self.env['sale.order.line'].search([('order_id', 'in', orders)])

                for line in lines:
                    val_com = val_com + line.price_subtotal

                esActivo = False

                if val_com >= meta:
                    activos = int(inv.anfitrion_id.activos_directos)
                    activos = activos + 1
                    inv.anfitrion_id.activos_directos = activos
                    esActivo = True
                else:
                    inactivos = int(inv.anfitrion_id.inactivos_directos)
                    inv.anfitrion_id.inactivos_directos = inactivos + 1

                
                inv._get_nivel(date_start, date_end, meta, process_id)

                nivel = 0

                if esActivo and inv.invitado_ids:

                    ComisionNivelTmp = self.env['comisiones.nivel.tmp']

                    n0 = ComisionNivelTmp.search_count([('partner_id', '=', inv.id), ('nivel', '=', 0)])
                    n1 = ComisionNivelTmp.search_count([('partner_id', '=', inv.id), ('nivel', '=', 1)])
                    n2 = ComisionNivelTmp.search_count([('partner_id', '=', inv.id), ('nivel', '=', 2)])
                    n3 = ComisionNivelTmp.search_count([('partner_id', '=', inv.id), ('nivel', '=', 3)])
                    n4 = ComisionNivelTmp.search_count([('partner_id', '=', inv.id), ('nivel', '=', 4)])

                    if n0 >= 1:
                        nivel = 1
                    if n1 >= 2:
                        nivel = 2
                    if n2 >= 3:
                        nivel = 3
                    if n3 >= 4:
                        nivel = 4
                    if n4 >= 5:
                        nivel = 5


                    vals = {
                        'process_id': process_id,
                        'partner_id': inv.anfitrion_id.id,
                        'partner_curr_id': inv.id,
                        'nivel': nivel,
                    }

                    nivel_reg = ComisionNivelTmp.search_count([('partner_id', '=', inv.id), ('partner_curr_id', '=', inv.anfitrion_id.id)])
                    
                    if nivel_reg == 0:
                        com = self.env['comisiones.nivel.tmp'].create(vals)

            #Hacer conteo de lista por niveles

            ComisionNivelTmp = self.env['comisiones.nivel.tmp']

            n0 = ComisionNivelTmp.search_count([('partner_id', '=', self.id), ('nivel', '=', 0)])
            n1 = ComisionNivelTmp.search_count([('partner_id', '=', self.id), ('nivel', '=', 1)])
            n2 = ComisionNivelTmp.search_count([('partner_id', '=', self.id), ('nivel', '=', 2)])
            n3 = ComisionNivelTmp.search_count([('partner_id', '=', self.id), ('nivel', '=', 3)])
            n4 = ComisionNivelTmp.search_count([('partner_id', '=', self.id), ('nivel', '=', 4)])

            if n0 >= 1:
                nivel = 1
            if n1 >= 2:
                nivel = 2
            if n2 >= 3:
                nivel = 3
            if n3 >= 4:
                nivel = 4
            if n4 >= 5:
                nivel = 5

            alias = self.env['ir.config_parameter'].search([('key','=','alias_nivel')])
            dicnivel = ast.literal_eval(alias.value)
            aliasnivel = dicnivel[nivel]

            if aliasnivel:
                self.nivel = aliasnivel
            else:
                self.nivel = nivel

    def _get_comisiones(self, partner_cr_id, subnivel, date_start=None, date_end=None, meta=0.0, process_id = 0):
        if not self.invitado_ids:
            val_com = 0
            orders = self.env['sale.order'].search([('partner_id', '=', self.id), ('date_order', '>=', date_start), ('date_order', '<=', date_end), ('state', '=', 'sale')]).ids
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
                            if not self.env['comisiones.comision'].search([('sale_line_id', '=', line.id), ('partner_id', '=', partner_cr_id)]):
                                com = self.env['comisiones.comision'].create(vals)                        
        else:

            subnivel = subnivel + 1

            for inv in self.invitado_ids:

                val_com = 0

                orders = self.env['sale.order'].search([('partner_id', '=', inv.id), ('date_order', '>=', date_start), ('date_order', '<=', date_end), ('state', '=', 'sale')]).ids
                lines = self.env['sale.order.line'].search([('order_id', 'in', orders)])

                for line in lines:
                    val_com = val_com + line.price_subtotal

                esActivo = False

                if val_com >= meta:
                    esActivo = True
                        
                inv._get_comisiones(partner_cr_id, subnivel, date_start, date_end, meta, process_id)

                if esActivo and inv.invitado_ids:

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
                                'partner_ori_id': inv.id,
                            }

                            if partner_cr_id != inv.id:
                                if not self.env['comisiones.comision'].search([('sale_line_id', '=', line.id), ('partner_id', '=', partner_cr_id)]):
                                    com = self.env['comisiones.comision'].create(vals)

    #--------- Funciones para la visualización en Portal  ---------

    def _compute_num_guests(self):
        for partner in self:
            partner.num_guests = len(partner.invitado_ids)

    def _compute_comisiones_por_pagar(self):
        for partner in self:
            partner.comisiones_por_pagar = sum(self.env['comisiones.comision'].search([('partner_id', '=', partner.id), ('state', '=', 'open')]).mapped('val_comision'))
    
    def _compute_amount_period(self):
        for partner in self:
            val_com = 0

            periodo = self.env['comisiones.periodo'].search([('active', '=', True)], limit=1)

            if periodo:
                valor_meta = periodo.amount_meta
                fecha_ini = periodo.date_start
                fecha_fin = periodo.date_end
            else:
                valor_meta = 0
                fecha_ini = '1900-01-01'
                fecha_fin = '1900-01-01'

            orders = self.env['sale.order'].search([('partner_id', '=', partner.id), ('date_order', '>=', fecha_ini), ('date_order', '<=', fecha_fin), ('state', '=', 'sale')]).ids
            lines = self.env['sale.order.line'].search([('order_id', 'in', orders)])

            
            for line in lines:
                val_com = val_com + line.price_subtotal

            partner.valor_periodo = val_com

            if valor_meta > 0:
                partner.cumplimiento = (val_com * 100) / valor_meta
            else:
                partner.cumplimiento = 0

    access_url = fields.Char(
        'Portal Access URL', compute='_compute_access_url',
        help='Customer Portal URL')

    def _compute_access_url(self):
        for record in self:
            record.access_url = '/my/guests/' + str(record.id)

    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        """
            Get a portal url for this model, including access_token.
            The associated route must handle the flags for them to have any effect.
            - suffix: string to append to the url, before the query string
            - report_type: report_type query string, often one of: html, pdf, text
            - download: set the download query string to true
            - query_string: additional query string
            - anchor: string to append after the anchor #
        """
        self.ensure_one()
        url = self.access_url
        return url

    def get_invitados(self, parents=None):
        if not parents:
            parents = self.env[self._name]

        indirect_subordinates = self.env[self._name]
        parents |= self
        direct_subordinates = self.invitado_ids - parents
        child_subordinates = direct_subordinates.get_invitados(parents=parents) if direct_subordinates else self.browse()
        indirect_subordinates |= child_subordinates
        return indirect_subordinates | direct_subordinates
