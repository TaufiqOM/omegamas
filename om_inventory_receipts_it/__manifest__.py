{
    'name': 'OM Inventory Receipts IT',
    'version': '1.0',
    'description': 'Implement Backdating for Inventory Receipts and Include Necessary Accounting Fields',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'depends': ['stock', 'om_purchase_order_it', 'om_purchase_manual_delivery', 'account', 'purchase', 'analytic', 'om_sale_it'],
    "data": [
        "views/stock_move_line_views.xml",
        "views/stock_picking_list_views.xml"
    ],
    'installable': True,
    'auto_install': False
}
