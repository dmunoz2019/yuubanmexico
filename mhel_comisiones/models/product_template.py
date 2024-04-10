# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplateExt(models.Model):
    _inherit = 'product.template'

    is_comisionable = fields.Boolean(string="Es producto comisionable?")
