{
    'name': "QR Client",
    'version': "1.0",
    'summary': "QR client to endpoint",
    'category': 'Tools',
    'author': "COMMIT",
    'website': "https://dmunoz2019.github.io/diegoweb/",
    'license': "AGPL-3",
    'depends': ['base', 'web', 'mhel_comisiones'],
    'data': [
        'views/contract_form.xml',
        'views/res_users.xml',
        'views/res_partner.xml',
        'views/portal.xml',
    ],
    'demo': [
    ],
    'assets' : {
        'web.assets_frontend ': [
            'client_qr/static/lib/jquery.validate.min.js',
        ],
        'web.assets_common': [
            'client_qr/static/lib/jquery.validate.min.js',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
