from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.exceptions import AccessDenied
import logging
from odoo.http import request
from io import BytesIO
import base64


import qrcode
_logger = logging.getLogger(__name__)




class ResUsers(models.Model):
    _inherit = 'res.users'
    # lets create a new field to store the qr code in the user, each user will have a qr code
    qr_code = fields.Binary(string='QR Code', readonly=True, compute='_generate_qr_code')

    @api.depends('name')  # Ajusta según necesites que otros campos disparen esta función
    def _generate_qr_code(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for user in self:
            # Asumiendo que tienes una ruta como '/my_view' en tu controlador que espera un parámetro 'user_id'
            full_url = f'{base_url}/contract_form?iddist={user.iddist}'
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(full_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            user.qr_code = qr_image


