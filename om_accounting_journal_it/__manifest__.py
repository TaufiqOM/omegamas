{
    'name': 'OM Accounting Journal IT',
    'version': '1.0',
    'summary': 'Summery',
    'description': 'Add Field Department to Journal Item',
    'category': 'Accounting',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'depends': ['account', 'stock', 'mrp', 'purchase', 'hr', 'om_purchase_order_it', 'om_inventory_receipts_it'],
    'data': [
        'views/account_move_line_views.xml'
    ],
    'installable': True,
    'auto_install': False
}
