# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _default_custom_warehouse_id(self):
        if self.env.user.default_warehouse_id:
            warehouse_ids = self.env.user.default_warehouse_id
        else:
            company = self.env.company.id
            warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    warehouse_id = fields.Many2one(default=_default_custom_warehouse_id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            if self.env.user.default_warehouse_id:
                self.warehouse_id = self.env.user.default_warehouse_id
            else:
                warehouse_id = self.env['ir.default'].get_model_defaults('sale.order').get('warehouse_id')
                self.warehouse_id = warehouse_id or self.env['stock.warehouse'].search(
                    [('company_id', '=', self.company_id.id)], limit=1)
