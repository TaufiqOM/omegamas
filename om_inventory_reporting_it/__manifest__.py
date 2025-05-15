{
    'name': 'OM Inventory Reporting IT',
    'version': '1.0',
    'description': 'Show Field Department, Proyek and Note',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'depends': ['stock', 'account', 'purchase', 'analytic', 'mrp', 'om_inventory_receipts_it'],
    "data": [
        "views/stock_valuation_layer_views.xml",
        "views/stock_move_line_list_views.xml",
    ],
    'installable': True,
    'auto_install': False
}
