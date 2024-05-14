{
    'name': "QR Client",
    'version': "1.0",
    'summary': "QR client to endpoint",
    'category': 'Tools',
    'author': "COMMIT",
    'website': "https://dmunoz2019.github.io/diegoweb/",
    'license': "AGPL-3",
    'depends': ['base', 'web'],
    'data': [
        'views/contract_form.xml',
        'views/res_users.xml',
        'views/res_partner.xml',
    ],
    'demo': [
    ],
    'external_dependencies': {
        'python': ['qrcode'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
