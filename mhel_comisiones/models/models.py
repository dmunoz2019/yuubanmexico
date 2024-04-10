# -*- coding: utf-8 -*-

from email.policy import default
from pickle import FALSE
from odoo import models, fields, api
from odoo.tools import float_round
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta, date, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import format_date
import uuid
import logging
import ast



import base64
from PyPDF2 import PdfFileWriter, PdfFileReader
import os
from tempfile import mkstemp
from PIL import Image


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

class ComisionesNivelTmp(models.TransientModel):

    _name = 'comisiones.nivel.tmp'
    _description = 'Calculo temporal de niveles'

    process_id = fields.Integer('ID Proceso')
    partner_id = fields.Integer('Cliente')
    partner_curr_id = fields.Integer('Cliente validado')
    nivel = fields.Integer('Nivel')

class ComisionesPorcentaje(models.Model):

    _name = 'comisiones.porcentaje'
    _description = 'Porcentajes de comisiones'

    subnivel = fields.Integer('Subnivel')
    por_comision = fields.Float('Porcentaje Comision')

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

class ComisionesPeriodo(models.Model):

    _name = 'comisiones.periodo'
    _description = 'Periodo para el calculo de comisiones por cliente'

    name = fields.Char(string='Periodo')
    amount_meta = fields.Float(string='Valor meta periodo')
    date_start = fields.Date(string='Fecha inicio')
    date_end = fields.Date(string='Fecha fin')
    active = fields.Boolean(string='Activo')

    @api.constrains('date_end')
    def _check_active(self):
        
        count = 0
        for record in self:
            if record.active:
                count = count + 1

        if count > 0:
            raise ValidationError("Solo puede tener un periodo activo para la liquidación de comisiones")


class ComisionesWizard(models.TransientModel):
    _name = 'comisiones.wizard'
    _description = 'Calcular comisiones por anfitrión'

    date_start = fields.Date('Fecha inicial')
    date_end = fields.Date('Fecha final')

    partner_ids = fields.Many2many('res.partner', 'comisiones_report_partner_rel', 'partner_id', 'comision_report_id', string='Terceros', copy=False)

    def action_calcular_niveles(self):

        partner_rec_ids = []

        periodo = self.env['comisiones.periodo'].search([('active', '=', True)], limit=1)

        if not periodo:
            raise ValidationError('No hay un periodo activo para liquidar comisiones')

        sales = self.env['sale.order'].search([('state', '=', 'sale'), ('date_order', '>=', periodo.date_start), ('date_order', '<=', periodo.date_end)])

        for sale in sales:
            partner_rec_ids.append(sale.partner_id.id)

        partners = self.env['res.partner'].search([('id', 'in', partner_rec_ids)])

        self.env['comisiones.nivel.tmp'].search([('process_id', '=', '1')]).unlink()

        for partner in partners:
            if periodo:
                partner._get_nivel(periodo.date_start, periodo.date_end, periodo.amount_meta, 1)


                alias = self.env['ir.config_parameter'].search([('key','=','alias_nivel')])
                dicnivel = ast.literal_eval(alias.value)
                aliasnivel = dicnivel[0]
                self.env['res.partner'].search([('nivel', '=', '0')]).write({'nivel':aliasnivel})

        for partner in partners:
            if periodo:
                if (partner.id in self.partner_ids.ids) or not self.partner_ids:
                        partner._get_comisiones(partner.id, 0, periodo.date_start, periodo.date_end, periodo.amount_meta, 1)


        return {'type': 'ir.actions.act_window_close'}

    def action_exit(self):
        return {'type': 'ir.actions.act_window_close'}



class ComisionesLiquidacionWizard(models.TransientModel):
    _name = 'comisiones.liquidacion.wizard'
    _description = 'Liquidar comisiones por anfitrión'

    partner_ids = fields.Many2many('res.partner', 'comisiones_liq_report_partner_rel', 'partner_id', 'comision_report_id', string='Terceros', copy=False)

    def action_liquidar_comisiones(self):

        if not self.partner_ids:
            comisiones = self.env['comisiones.comision'].search([('state', '=', 'open')])
        else:
            comisiones = self.env['comisiones.comision'].search([('state', '=', 'open'), ('partner_id', 'in', self.partner_ids.ids)])
            
        for comision in comisiones:
            comision.state = 'paid'
            user = self.env['res.users'].browse(self._context['uid'])
            comision.liquidador_id = user
            comision.date_liquidacion = fields.Date.today()

        return {'type': 'ir.actions.act_window_close'}

    def action_exit(self):
        return {'type': 'ir.actions.act_window_close'}

class ProductTemplateExt(models.Model):

    _inherit = 'product.template'

    is_comisionable = fields.Boolean(string="Es producto comisionable?")
    

class SaleOrderLineExt(models.Model):

    _inherit = 'sale.order'

    val_comisionable = fields.Float(string='Valor comisionable', store=True, readonly=True, compute='_compute_amount_comisionable')
    

    @api.depends('amount_total', 'currency_id', 'order_line')
    def _compute_amount_comisionable(self):
        for order in self:

            val_comisionable = 0

            for line in order.order_line:
                if line.is_comisionable:
                    val_comisionable = val_comisionable + (line.product_uom_qty * line.price_unit)
            
            order.update({
                    'val_comisionable': val_comisionable,
                })                

class SaleOrderLineExt(models.Model):

    _inherit = 'sale.order.line'

    is_comisionable = fields.Boolean(string="Es comisionable?")
    
    @api.onchange('product_id')
    def _onchange_producto(self):

        if self.product_id.product_tmpl_id.is_comisionable is True:
            self.is_comisionable = True
        else:
            self.is_comisionable = False
