# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Manual Delivery",
    "category": "Sale",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "summary": "Create manually your deliveries",
    "depends": ["stock_delivery", "sale_stock", "sales_team", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/crm_team.xml",
        "views/sale_order.xml",
        "views/res_config_view.xml",
        "views/move_views.xml",
        "wizard/manual_delivery.xml",
        "wizard/stock_picking_return.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "pre_init_hook": "pre_init_hook",
}
