{
    'name': "Custom Authentication",
    'version': "1.0",
    'summary': "Permite la autenticación utilizando el campo 'login' o 'ref'.",
    'category': 'Authentication',
    'author': "Tu Nombre o Empresa",
    'website': "https://tusitio.com",
    'license': "AGPL-3",
    'depends': ['base', 'web', 'yuuban_custom' ],
    'data': [
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'description': """
Custom Authentication Module
============================
Este módulo permite que los usuarios se autentiquen usando el campo 'login' estándar o un campo 'ref' alternativo.
Las contraseñas son verificadas de la manera estándar, y se puede usar cualquiera de los dos campos como identificador de usuario.
""",
}
