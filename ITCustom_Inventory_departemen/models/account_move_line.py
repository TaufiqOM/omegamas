from odoo import fields, models, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order"

    department_id = fields.Many2one(
        related='purchase_request_lines.department_id',
        string='Department',
        store=True,
        readonly=True
    )