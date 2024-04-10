# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    comisiones_valor_meta = fields.Float(
        string="Valor meta por período",
        default=3500,
        config_parameter='comisiones.valor.meta',
    )
    comisiones_primer_nivel = fields.Float(
        string="Comisiones 1er nivel",
        default=35,
        config_parameter='comisiones.primer.nivel',
    )
    comisiones_segundo_nivel = fields.Float(
        string="Comisiones 2do nivel",
        default=15,
        config_parameter='comisiones.segundo.nivel',
    )
    comisiones_tercer_nivel = fields.Float(
        string="Comisiones 3er nivel",
        default=3,
        config_parameter='comisiones.tercer.nivel',
    )
    comisiones_cuarto_nivel = fields.Float(
        string="Comisiones 4to nivel",
        default=2,
        config_parameter='comisiones.cuarto.nivel',
    )
    comisiones_quinto_nivel = fields.Float(
        string="Comisiones 5to nivel",
        default=5,
        config_parameter='comisiones.quinto.nivel',
    )

