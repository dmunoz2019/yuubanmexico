# -*- coding: utf-8 -*-

import io
import xlsxwriter
import base64

from datetime import time, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

# log 
import logging
_logger = logging.getLogger(__name__)



class WizardReporteComision(models.TransientModel):
    _name = 'wizard.reporte.comision'

    periodo_id = fields.Many2one(
        comodel_name='comisiones.periodo',
        string='Periodo',
        context={"active_test": False}
    )
    filecontent = fields.Binary(string='Archivo')

    def computar_comisiones(self, date_cut = True):
        data = []
        tz_offset = int(self.env.user.tz_offset.replace('-', '').replace('0', ''))
        sale_ids = self.env['sale.order']
        if date_cut:
            date_start = datetime.combine(self.periodo_id.date_start, time(0, 0, 0)) + relativedelta(hours=tz_offset)
            date_end = datetime.combine(self.periodo_id.date_end, time(0, 0, 0)) + relativedelta(days=1, hours=tz_offset)
            sale_ids = self.env['sale.order'].search([
                ('state', '=', 'sale'),
                ('date_order', '>=', date_start),
                ('date_order', '<=', date_end)
            ])
        elif not date_cut:
            sale_ids = self.env['sale.order'].search([
                ('state', '=', 'sale')
            ])
        partner_ids = sale_ids.mapped('partner_id')
        comisiones_valor_meta = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.valor.meta', 3500))
        por_comision_nivel1 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.primer.nivel', 35))
        por_comision_nivel2 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.segundo.nivel', 15))
        por_comision_nivel3 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.tercer.nivel', 3))
        por_comision_nivel4 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.cuarto.nivel', 2))
        por_comision_nivel5 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.quinto.nivel', 5))
        
        for partner_id in partner_ids.sorted(key=lambda x: x.name):
            comision = self.env['comisiones.comision'].calcular_comisiones(
                partner_id,
                sale_ids,
                self.periodo_id,
                comisiones_valor_meta,
                por_comision_nivel1,
                por_comision_nivel2,
                por_comision_nivel3,
                por_comision_nivel4,
                por_comision_nivel5,
            )
            if comision:
                data += comision

        return data
    def consolidar_comisiones(self, data):
            consolidado = {}
            for record in data:
                if record['partner_id'] not in consolidado:
                    consolidado[record['partner_id']] = {
                        'total_ventas': 0,
                        'nivel1': 0,
                        'nivel2': 0,
                        'nivel3': 0,
                        'nivel4': 0,
                        'nivel5': 0,
                        'count_nivel1': 0,
                        'count_nivel2': 0,
                        'count_nivel3': 0,
                        'count_nivel4': 0,
                        'count_nivel5': 0,

                    }
                if record['nivel'] == 1:
                    consolidado[record['partner_id']]['nivel1'] += record['val_comision']
                    consolidado[record['partner_id']]['count_nivel1'] += 1
                    consolidado[record['partner_id']]['total_ventas'] += record['amount_comision']
                elif record['nivel'] == 2:
                    consolidado[record['partner_id']]['nivel2'] += record['val_comision']
                    consolidado[record['partner_id']]['count_nivel2'] += 1
                    consolidado[record['partner_id']]['total_ventas'] += record['amount_comision']
                elif record['nivel'] == 3:
                    consolidado[record['partner_id']]['nivel3'] += record['val_comision']
                    consolidado[record['partner_id']]['count_nivel3'] += 1
                    consolidado[record['partner_id']]['total_ventas'] += record['amount_comision']
                elif record['nivel'] == 4:
                    consolidado[record['partner_id']]['nivel4'] += record['val_comision']
                    consolidado[record['partner_id']]['count_nivel4'] += 1
                    consolidado[record['partner_id']]['total_ventas'] += record['amount_comision']
                elif record['nivel'] == 5:
                    consolidado[record['partner_id']]['nivel5'] += record['val_comision']
                    consolidado[record['partner_id']]['count_nivel5'] += 1
                    consolidado[record['partner_id']]['total_ventas'] += record['amount_comision']
            return consolidado
    # def consolidar_comisiones(self, data, tipo='nivel'):
    #     consolidado = {}
    #     for record in data:
    #         if tipo == 'nivel':
    #             if record['partner_id'] not in consolidado:
    #                 consolidado[record['partner_id']] = {
    #                     'nivel1': 0,
    #                     'nivel2': 0,
    #                     'nivel3': 0,
    #                     'nivel4': 0,
    #                     'nivel5': 0,
    #                 }
    #             if record['nivel'] == 1:
    #                 consolidado[record['partner_id']]['nivel1'] += record['val_comision']
    #             elif record['nivel'] == 2:
    #                 consolidado[record['partner_id']]['nivel2'] += record['val_comision']
    #             elif record['nivel'] == 3:
    #                 consolidado[record['partner_id']]['nivel3'] += record['val_comision']
    #             elif record['nivel'] == 4:
    #                 consolidado[record['partner_id']]['nivel4'] += record['val_comision']
    #             elif record['nivel'] == 5:
    #                 consolidado[record['partner_id']]['nivel5'] += record['val_comision']

    #     return consolidado



    def generar_reporte(self):
        data = self.computar_comisiones()
        consolidado = self.consolidar_comisiones(data)

        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = wb.add_worksheet('Reporte')

        titulo_style = wb.add_format({
            'font_name': 'Calibri',
            'font_size': 18,
            'bold': True,
        })

        cabecera_style = wb.add_format({
            'bold': True,
            'font_size': 13,
        })

        currency_style = wb.add_format({
            'num_format': '$#,##0.00',
        })

        currency_bold_style = wb.add_format({
            'num_format': '$#,##0.00',
            'bold': True,
        })

        ws.write(0, 0, self.env.company.name, titulo_style)
        ws.write(2, 0, 'Periodo', cabecera_style)
        ws.write(2, 1, self.periodo_id.name)

        ws.write(4, 0, 'Nombre', cabecera_style)
        ws.write(4, 1, 'Total Ventas', cabecera_style)
        ws.write(4, 2, 'Nivel 1', cabecera_style)
        ws.write(4, 3, 'Líderes', cabecera_style)
        ws.write(4, 4, 'Nivel 2', cabecera_style)
        ws.write(4, 5, 'Líderes', cabecera_style)
        ws.write(4, 6, 'Nivel 3', cabecera_style)
        ws.write(4, 7, 'Líderes', cabecera_style)
        ws.write(4, 8, 'Nivel 4', cabecera_style)
        ws.write(4, 9, 'Líderes', cabecera_style)
        ws.write(4, 10, 'Nivel 5', cabecera_style)
        ws.write(4, 11, 'Líderes', cabecera_style)
        ws.write(4, 12, 'Total Comisiones', cabecera_style)

        row = 5
        for element in consolidado:
            ws.write(row, 0, self.env['res.partner'].browse(element).name)
            ws.write(row, 1, consolidado[element]['total_ventas'], currency_style)
            ws.write(row, 2, consolidado[element]['nivel1'], currency_style)
            ws.write(row, 3, consolidado[element]['count_nivel1'])
            ws.write(row, 4, consolidado[element]['nivel2'], currency_style)
            ws.write(row, 5, consolidado[element]['count_nivel2'])
            ws.write(row, 6, consolidado[element]['nivel3'], currency_style)
            ws.write(row, 7, consolidado[element]['count_nivel3'])
            ws.write(row, 8, consolidado[element]['nivel4'], currency_style)
            ws.write(row, 9, consolidado[element]['count_nivel4'])
            ws.write(row, 10, consolidado[element]['nivel5'], currency_style)
            ws.write(row, 11, consolidado[element]['count_nivel5'])
            ws.write(row, 12, consolidado[element]['nivel1'] + consolidado[element]['nivel2'] + consolidado[element]['nivel3'] + consolidado[element]['nivel4'] + consolidado[element]['nivel5'], currency_bold_style)
            row += 1

        ws.set_column('A:A', 45)
        ws.set_column('B:G', 15)

        wb.close()
        output.seek(0)
        data = output.read()

        if data:
            self.filecontent = base64.b64encode(data)
            filename_field = 'Comisiones{0}'.format(self.periodo_id.name)

            if self.filecontent:
                return {
                    'res_model': 'ir.actions.act_url',
                    'type': 'ir.actions.act_url',
                    'target': 'new',
                    'url': (
                        'web/content/?model=wizard.reporte.comision'
                        '&id={0}'
                        '&filename_field={1}'
                        '&field=filecontent'
                        '&download=true'
                        '&filename={1}.xlsx'.format(
                            self.id,
                            filename_field
                        )
                    ),
                }
            else:
                raise UserError('Hubo un error en la descarga')



    # def generar_reporte(self):
    #     data = []
    #     consolidado = {}
    #     tz_offset = int(self.env.user.tz_offset.replace('-', '').replace('0', ''))
    #     date_start = datetime.combine(self.periodo_id.date_start, time(0, 0, 0)) + relativedelta(hours=tz_offset)
    #     date_end = datetime.combine(self.periodo_id.date_end, time(0, 0, 0)) + relativedelta(days=1, hours=tz_offset)
    #     sale_ids = self.env['sale.order'].search([
    #         ('state', '=', 'sale'),
    #         ('date_order', '>=', date_start),
    #         ('date_order', '<=', date_end)
    #     ])
    #     partner_ids = sale_ids.mapped('partner_id')
    #     comisiones_valor_meta = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.valor.meta', 3500))
    #     por_comision_nivel1 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.primer.nivel', 35))
    #     por_comision_nivel2 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.segundo.nivel', 15))
    #     por_comision_nivel3 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.tercer.nivel', 3))
    #     por_comision_nivel4 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.cuarto.nivel', 2))
    #     por_comision_nivel5 = float(self.env['ir.config_parameter'].sudo().get_param('comisiones.quinto.nivel', 5))
    #     for partner_id in partner_ids.sorted(key=lambda x: x.name):
    #         comision = self.env['comisiones.comision'].calcular_comisiones(
    #             partner_id,
    #             sale_ids,
    #             self.periodo_id,
    #             comisiones_valor_meta,
    #             por_comision_nivel1,
    #             por_comision_nivel2,
    #             por_comision_nivel3,
    #             por_comision_nivel4,
    #             por_comision_nivel5,
    #         )
    #         if comision:
    #             data += comision
    #     _logger.info('--------------------------------------------------------------------------------')
    #     _logger.info('--------------------------------------------------------------------------------')
    #     _logger.info('data: %s', data)
    #     _logger.info('--------------------------------------------------------------------------------')
    #     _logger.info('--------------------------------------------------------------------------------')
    #     if data:
    #         for record in data:
    #             if record['partner_id'] not in consolidado:
    #                 consolidado[record['partner_id']] = {
    #                     'nivel1': 0,
    #                     'nivel2': 0,
    #                     'nivel3': 0,
    #                     'nivel4': 0,
    #                     'nivel5': 0,
    #                 }
    #             if record['nivel'] == 1:
    #                 consolidado[record['partner_id']]['nivel1'] += record['val_comision']
    #             elif record['nivel'] == 2:
    #                 consolidado[record['partner_id']]['nivel2'] += record['val_comision']
    #             elif record['nivel'] == 3:
    #                 consolidado[record['partner_id']]['nivel3'] += record['val_comision']
    #             elif record['nivel'] == 4:
    #                 consolidado[record['partner_id']]['nivel4'] += record['val_comision']
    #             elif record['nivel'] == 5:
    #                 consolidado[record['partner_id']]['nivel5'] += record['val_comision']
    #     _logger.info('--------------------------------------------------------------------------------')
    #     _logger.info('--------------------------------------------------------------------------------')
    #     _logger.info('consolidado: %s', consolidado)
    #     _logger.info('--------------------------------------------------------------------------------')
    #     _logger.info('--------------------------------------------------------------------------------')
    #     output = io.BytesIO()
    #     wb = xlsxwriter.Workbook(output, {'in_memory': True})
    #     ws = wb.add_worksheet('Reporte')

    #     titulo_style = wb.add_format({
    #         'font_name': 'Calibri',
    #         'font_size': 18,
    #         'bold': True,
    #     })
    #     cabecera_style = wb.add_format({
    #         'bold': True,
    #         'font_size': 13,
    #     })
    #     currency_style = wb.add_format({
    #         'num_format': '$#,##0.00',
    #     })
    #     currency_bold_style = wb.add_format({
    #         'num_format': '$#,##0.00',
    #         'bold': True,
    #     })

    #     ws.write(0, 0, self.env.company.name, titulo_style)
    #     ws.write(2, 0, 'Periodo'.format(self.env.company.name), cabecera_style)
    #     ws.write(2, 1, self.periodo_id.name)

    #     ws.write(4, 0, 'Nombre', cabecera_style)
    #     ws.write(4, 1, 'Nivel 1', cabecera_style)
    #     ws.write(4, 2, 'Nivel 2', cabecera_style)
    #     ws.write(4, 3, 'Nivel 3', cabecera_style)
    #     ws.write(4, 4, 'Nivel 4', cabecera_style)
    #     ws.write(4, 5, 'Nivel 5', cabecera_style)
    #     ws.write(4, 6, 'Total', cabecera_style)

    #     row = 5
    #     for element in consolidado:
    #         ws.write(row, 0, self.env['res.partner'].browse(element).name)
    #         ws.write(row, 1, consolidado[element]['nivel1'], currency_style)
    #         ws.write(row, 2, consolidado[element]['nivel2'], currency_style)
    #         ws.write(row, 3, consolidado[element]['nivel3'], currency_style)
    #         ws.write(row, 4, consolidado[element]['nivel4'], currency_style)
    #         ws.write(row, 5, consolidado[element]['nivel5'], currency_style)
    #         ws.write(row, 6, consolidado[element]['nivel1'] + consolidado[element]['nivel2'] + consolidado[element]['nivel3'] + consolidado[element]['nivel4'] + consolidado[element]['nivel5'], currency_bold_style)
    #         row += 1

    #     ws.set_column('A:A', 45)
    #     ws.set_column('B:G', 15)

    #     wb.close()
    #     output.seek(0)
    #     data = output.read()

    #     if data:
    #         self.filecontent = base64.b64encode(data)
    #         filename_field = 'Comisiones{0}'.format(self.periodo_id.name)

    #         if self.filecontent:
    #             return{
    #                 'res_model': 'ir.actions.act_url',
    #                 'type': 'ir.actions.act_url',
    #                 'target': 'new',
    #                 'url': (
    #                     'web/content/?model=wizard.reporte.comision'
    #                     '&id={0}'
    #                     '&filename_field={1}'
    #                     '&field=filecontent'
    #                     '&download=true'
    #                     '&filename={1}.xlsx'.format(
    #                         self.id,
    #                         filename_field
    #                     )
    #                 ),
    #             }
    #         else:
    #             raise UserError('Hubo un error en la descarga')

