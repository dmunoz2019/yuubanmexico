from odoo import models, fields

class UserBadge(models.Model):
    _name = 'user.badge'
    _description = 'Badge Asignado a Usuario'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(string='Nombre del Badge', required=True)
    user_id = fields.Many2one('res.users', string='Usuario', required=True)
    badge_id = fields.Many2one('sale.badge', string='Badge', required=True)
    badge_image = fields.Binary(string='Imagen del Badge', related='badge_id.badge_image')
    sales_volume = fields.Float(string='Volumen de Ventas', required=True)
    period_start = fields.Date(string='Inicio del Período', required=True)
    period_end = fields.Date(string='Fin del Período', required=True)
    date_start = fields.Date("Start Date")
    date_end = fields.Date("End Date")
    description = fields.Text("Description")
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], string='Priority', default='1')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')], string='State', default='draft')
    stage_ids = fields.One2many('user.badge.stage', 'user_badge_id', string='User badge Stages')
    label_ids = fields.Many2many('user.badge.tag', 'user_badge_tag_rel', 'tag_id', 'user_badge_ids', string='User badge Tags')

class UserBadgeStage(models.Model):
    _name = 'user.badge.stage'
    _description = 'User.badge Stage'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(string='Sequence', required=True)
    probability = fields.Float(string='Probability (%)', required=True)
    user_badge_id = fields.Many2one('user.badge', string='User badge', required=True)

class UserBadgeTag(models.Model):
    _name = 'user.badge.tag'
    _description = 'User.badge Tag'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index', required=True)
    user_badge_ids = fields.Many2many('user.badge', 'user_badge_tag_rel', 'user_badge_ids', 'tag_id', string='User badge Tags')