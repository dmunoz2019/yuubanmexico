# -*- coding: utf-8 -*-
{
    'name': "Comisiones Multinivel",
    'summary': "Relacion de comisiones por anfitrión y arbol de invitados",
    'description': "Relacion de comisiones por anfitrión y arbol de invitados",
    'author': "Sebastian Ramirez",
    'website': "sebasramirezn@gmail.com",
    'category': 'Sales',
    'version': '0.1',
    'depends': [
        'base',
        'sale_management',
        'sale',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/comisiones_portal.xml',
        'views/reports_template.xml',
        'views/reports.xml',
        'views/sale_order_views.xml',
        'views/comisiones_periodo_views.xml',
        'views/product_template_views.xml',
        'wizard/comisiones_liquidacion_wizard_views.xml',
        'wizard/comisiones_wizard_views.xml',
        'views/sale_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/wizard_reporte_comision_views.xml',
    ],

}
