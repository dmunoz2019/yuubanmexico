from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.exceptions import AccessDenied
import logging
from odoo.http import request
import pytz

_logger = logging.getLogger(__name__)




class ResUsers(models.Model):
    _inherit = 'res.users'

    iddist = fields.Char("Id de Cliente",  related='partner_id.iddist', readonly=False)

    @classmethod
    def _login(cls, db, login, password,user_agent_env):
        """ Authenticate based on either login or ref, and verify the password """
        if not password:
            raise AccessDenied()
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        if login:
            if login.find('@') == -1:
                login = login.lower()
            user = request.env['res.users'].sudo().search([('iddist', '=', login)], limit=1)
            if user:
                login = user.login
                _logger.info('ID:', login)
            else:
                user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
                if user:
                    login = user.login
                    _logger.info('LOGIN:', login)
        try:
            _logger.info('IP:', ip)
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                with self._assert_can_auth(user=login):
                    user = self.search(self._get_login_domain(login), order=self._get_login_order(), limit=1)
                    if not user:
                        raise AccessDenied()
                    user = user.with_user(user)
                    user._check_credentials(password, user_agent_env)
                    tz = request.httprequest.cookies.get('tz') if request else None
                    if tz in pytz.all_timezones and (not user.tz or not user.login_date):
                        # first login or missing tz -> set tz to browser tz
                        user.tz = tz
                    user._update_last_login()
        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
            raise
        _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)

        return user.id