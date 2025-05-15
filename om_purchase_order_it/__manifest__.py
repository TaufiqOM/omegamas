{
    'name': 'OM Purchase Order IT',
    'version': '1.0',
    'description': 'Create Sequential Draft-XX for Manual Stock Picking and Add Required Accounting Fields',
    'category': 'Purchase Order',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'depends': ['purchase', 'om_purchase_manual_delivery', 'account', 'stock', 'mrp'],
    "data": [
            "security/ir.model.access.csv",
            "views/purchase_order_line_views.xml",
            "views/purchase_order_list_views.xml",
            "views/purchase_order_views.xml",
            "wizard/purchase_order_discount_views.xml"
        ],
    'installable': True,
    'auto_install': False
}