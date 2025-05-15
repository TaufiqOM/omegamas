{
    'name': 'OM Sales Blanket Order IT',
    'version': '1.0',
    'description': 'Create Backdate Feature and Add Required Sales Field in Blanket Order',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'depends': ['sale_blanket_order', 'account', 'stock', 'om_sale_external_id'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_blanket_order_line_views.xml',
        'views/sale_blanket_order_views.xml',
        'views/sale_blanket_order_tree.xml',
        'wizard/sale_blanket_order_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}
