from odoo import fields, models, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    new_field = fields.Char(string="New Column", compute="_compute_department_id", store=True)
    department_id = fields.Many2one('hr.department', string="Department", compute="_compute_department_id", store=True)

    @api.depends('product_id', 'order_id')
    def _compute_department_id(self):
        for line in self:
            # Ambil department_id dari purchase.request.line
            purchase_request_line = self.env['purchase.request.line'].search([
                ('product_id', '=', line.product_id.id),
                ('request_id.state', '=', 'approved')
            ], limit=1)
            line.department_id = purchase_request_line.department_id
            line.new_field = purchase_request_line.department_id.name if purchase_request_line.department_id else ''