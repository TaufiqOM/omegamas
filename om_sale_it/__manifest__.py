{
    'name': 'OM Sales Order IT',
    'version': '1.0',
    'description': 'Add Required Sales Fields in Sales Order',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'depends': ['sale', 'stock', 'om_sale_blanket_order_it'],
    'data': [
        'views/sale_order_views.xml',
        'views/sale_order_form_line_views.xml',
        'views/sale_order_tree_closed_views.xml',
    ],
    'installable': True,
    'application': False,
}
