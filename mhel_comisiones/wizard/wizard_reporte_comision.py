# -*- coding: utf-8 -*-

import io
import xlsxwriter
import base64

from datetime import time, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class WizardReporteComision(models.TransientModel):
    _name = 'wizard.reporte.comision'

    periodo_id = fields.Many2one(
        comodel_name='comisiones.periodo',
        string='Periodo',
        context={"active_test": False}
    )
    filecontent = fields.Binary(string='Archivo')

    def generar_reporte(self):
        data = []
        consolidado = {}
        tz_offset = int(self.env.user.tz_offset.replace('-', '').replace('0', ''))
        date_start = datetime.combine(self.periodo_id.date_start, time(0, 0, 0)) + relativedelta(hours=tz_offset)
        date_end = datetime.combine(self.periodo_id.date_end, time(0, 0, 0)) + relativedelta(days=1, hours=tz_offset)
        sale_ids = self.env['sale.order'].search([
            ('state', '=', 'sale'),
            ('date_order', '>=', date_start),
            ('date_order', '<=', date_end)
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
        ws.write(2, 0, 'Periodo'.format(self.env.company.name), cabecera_style)
        ws.write(2, 1, self.periodo_id.name)

        ws.write(4, 0, 'Nombre', cabecera_style)
        ws.write(4, 1, 'Nivel 1', cabecera_style)
        ws.write(4, 2, 'Nivel 2', cabecera_style)
        ws.write(4, 3, 'Nivel 3', cabecera_style)
        ws.write(4, 4, 'Nivel 4', cabecera_style)
        ws.write(4, 5, 'Nivel 5', cabecera_style)
        ws.write(4, 6, 'Total', cabecera_style)

        row = 5
        for element in consolidado:
            ws.write(row, 0, self.env['res.partner'].browse(element).name)
            ws.write(row, 1, consolidado[element]['nivel1'], currency_style)
            ws.write(row, 2, consolidado[element]['nivel2'], currency_style)
            ws.write(row, 3, consolidado[element]['nivel3'], currency_style)
            ws.write(row, 4, consolidado[element]['nivel4'], currency_style)
            ws.write(row, 5, consolidado[element]['nivel5'], currency_style)
            ws.write(row, 6, consolidado[element]['nivel1'] + consolidado[element]['nivel2'] + consolidado[element]['nivel3'] + consolidado[element]['nivel4'] + consolidado[element]['nivel5'], currency_bold_style)
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
                return{
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

