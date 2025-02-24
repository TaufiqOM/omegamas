{
    'name': 'Custom Edit Picking Name',
    'version': '1.0',
    'summary': 'Memungkinkan edit field name pada stock.picking',
    'category': 'Inventory',
    'author': 'Taufiqur Rahman',
    'depends': ['stock', 'purchase'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
