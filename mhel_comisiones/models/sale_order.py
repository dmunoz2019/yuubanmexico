# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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

    val_comisionable = fields.Float(
        string='Valor comisionable',
        store=True,
        compute='_compute_amount_comisionable',
    )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_comisionable = fields.Boolean(string="Es comisionable?")

    @api.onchange('product_id')
    def _onchange_producto(self):
        self.is_comisionable = self.product_id.is_comisionable
