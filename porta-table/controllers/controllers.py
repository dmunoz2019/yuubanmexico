from odoo import http, fields
from odoo.http import request


class CommissionController(http.Controller):
    @http.route('/get_commissions', type='http', auth='user')
    def get_commissions(self):
        commissions = request.env['comisiones.comision'].search([])
        comi = []

        return request.render('porta-table.commisiones', {
            'commissions': commissions
        })
