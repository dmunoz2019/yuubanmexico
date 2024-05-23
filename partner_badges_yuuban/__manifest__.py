{
    'name': 'Partner Badges Yuuban',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Assign badges to users based on their sales volume over a configurable period.',
    'description': """
        This module assigns badges to users based on their total sales volume over a configurable period.
        It ensures that badges can only be upgraded and not downgraded in subsequent periods.
    """,
    'author': 'Your Name',
    'website': 'http://www.yourcompany.com',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'data/cron_jobs.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
