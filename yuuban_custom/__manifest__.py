# -*- coding: utf-8 -*-
{
    'name': "Personalizaciones YUUBAN",

    'summary': """
        Personalizaciones para red de ventas
        """,

    'description': """
        Personalizaciones para red de ventas 
    """,

    'author': "Cyber World Servicios Integrales",

    'category': 'other',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['contacts', 'base', 'sale'],

    # always loaded
    'data': [
        'views/campos_vistas.xml',
        'views/ir_sequence_view.xml',

    ],

    'application': True,
    'installable': True,
}
