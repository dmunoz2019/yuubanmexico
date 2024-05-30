# models/sale_badge.py
from odoo import models, fields

class SaleBadge(models.Model):
    _name = 'sale.badge'
    _description = 'Badge de Ventas'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Nombre del Badge', required=True)
    sales_target = fields.Float(string='Meta de Ventas', required=True)
    level = fields.Char(string='Nivel', required=True)
    level_id = fields.Many2one('badge.level', string='Level')
    period_start = fields.Date(string='Inicio del Periodo', required=False)
    period_end = fields.Date(string='Fin del Periodo', required=False)
    period_length = fields.Integer(string='Longitud del Período (meses)', required=True, default=3)
    badge_image = fields.Binary(string='Imagen del Badge')
    date_start = fields.Date("Start Date")
    date_end = fields.Date("End Date")
    description = fields.Text("Description")
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')], string='State', default='draft')
    stage_ids = fields.One2many('sale.badge.stage', 'sale_badge_id', string='Sale badge Stages')
    label_ids = fields.Many2many('sale.badge.tag', 'sale_badge_tag_rel', 'tag_id', 'sale_badge_ids', string='Sale.badge Tags')
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], string='Priority', default='1')
    user_id = fields.Many2one('res.users', string='Usuario', required=False)
    user_ids = fields.Many2many('res.users', string='Usuarios')

    def set_to_open(self):
        self.state = 'open'
    
    def set_to_done(self):
        self.state = 'done'
    
    def set_to_draft(self):
        self.state = 'draft'

class SaleBadgeStage(models.Model):
    _name = 'sale.badge.stage'
    _description = 'Sale.badge Stage'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(string='Sequence', required=True)
    probability = fields.Float(string='Probability (%)', required=True)
    sale_badge_id = fields.Many2one('sale.badge', string='Sale.badge', required=True)

class SaleBadgeTag(models.Model):
    _name = 'sale.badge.tag'
    _description = 'Sale badge Tag'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index', required=True)
    sale_badge_ids = fields.Many2many('sale.badge', 'sale_badge_tag_rel', 'sale_badge_ids', 'tag_id', string='Sale.badge Tags')
