# -*- coding: utf-8 -*-

from odoo import api, models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    default_warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string="Almacén por defecto",
    )