# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Manual Delivery",
    "summary": """
        Prevents pickings to be auto generated upon Purchase Order confirmation
        and adds the ability to manually generate them as the supplier confirms
        the different purchase order lines.
    """,
    "version": "18.0.1.1.5",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L.," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/create_manual_stock_picking.xml",
        "wizard/stock_picking_return.xml",
        "views/purchase_order_views.xml",
        "views/res_config_view.xml",
        "views/move_views.xml",
    ],
}

# {
#     "name": "Purchase Down Payment",
#     "version": "18.0.1.0.0",
#     "summary": "Option to create down payment from purchase order",
#     "author": "Elico Corp, Ecosoft, Odoo Community Association (OCA)",
#     "website": "https://github.com/OCA/purchase-workflow",
#     "category": "Purchase Management",
#     "license": "AGPL-3",
#     "depends": ["purchase"],
#     "data": [
#         "security/ir.model.access.csv",
#         "wizard/purchase_make_invoice_advance_views.xml",
#         "views/res_config_settings_views.xml",
#         "views/purchase_view.xml",
#     ],
#     "installable": True,
#     "auto_install": False,
# }

