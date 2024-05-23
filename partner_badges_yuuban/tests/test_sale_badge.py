# tests/test_sale_badge.py
from odoo.tests import common
from datetime import timedelta
from odoo import fields

class TestSaleBadge(common.TransactionCase):

    def setUp(self):
        super(TestSaleBadge, self).setUp()
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
        })
        self.badge1 = self.env['sale.badge'].create({
            'name': 'Bronze Badge',
            'sales_target': 1000.0,
            'level': 1,
        })
        self.badge2 = self.env['sale.badge'].create({
            'name': 'Silver Badge',
            'sales_target': 2000.0,
            'level': 2,
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
        })

    def create_invoice(self, amount_total):
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.user.partner_id.id,
            'invoice_date': fields.Date.today() - timedelta(days=10),
        })
        self.env['account.move.line'].create({
            'move_id': invoice.id,
            'product_id': self.product.id,
            'quantity': amount_total / self.product.list_price,
            'price_unit': self.product.list_price,
            'name': self.product.name,
        })
        invoice.action_post()
        return invoice

    def test_sales_evaluation(self):
        self.create_invoice(1500.0)
        self.user._evaluate_sales()
        badge = self.env['user.badge'].search([('user_id', '=', self.user.id)])
        self.assertEqual(len(badge), 1)
        self.assertEqual(badge.badge_id, self.badge1)

    def test_no_badge_for_low_sales(self):
        self.create_invoice(500.0)
        self.user._evaluate_sales()
        badge = self.env['user.badge'].search([('user_id', '=', self.user.id)])
        self.assertEqual(len(badge), 0)

    def test_upgrade_badge(self):
        self.create_invoice(2500.0)
        self.user._evaluate_sales()
        badge = self.env['user.badge'].search([('user_id', '=', self.user.id)])
        self.assertEqual(len(badge), 1)
        self.assertEqual(badge.badge_id, self.badge2)

    def test_no_downgrade_badge(self):
        self.create_invoice(2500.0)
        self.user._evaluate_sales()
        badge = self.env['user.badge'].search([('user_id', '=', self.user.id)])
        self.assertEqual(len(badge), 1)
        self.assertEqual(badge.badge_id, self.badge2)

        # Crear una nueva factura con menor total de ventas
        self.create_invoice(1500.0)
        self.user._evaluate_sales()
        badge = self.env['user.badge'].search([('user_id', '=', self.user.id)])
        self.assertEqual(len(badge), 1)
        self.assertEqual(badge.badge_id, self.badge2)  # Asegurar que no se baja el nivel de insignia
