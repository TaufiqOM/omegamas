{
    'name': 'MRP Production Custom Sequence',
    'version': '1.0',
    'summary': 'Modify sequence in MRP Production to use date_start',
    'description': 'This module modifies the MRP production sequence so that the prefix is taken from the UI, but the date is taken from date_start.',
    'category': 'Manufacturing',
    'author': 'Taufiqur Rahman',
    'depends': ['mrp', 'account'],
    'data': [
        'views/mrp_production_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
