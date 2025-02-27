from odoo import fields, models, api

class StockMove(models.Model):
    _inherit = "stock.move"

    department_id = fields.Many2one('hr.department', string="Department", compute="_compute_department_id", store=True)

    @api.depends('purchase_line_id')
    def _compute_department_id(self):
        for move in self:
            if move.purchase_line_id:
                move.department_id = move.purchase_line_id.department_id
            else:
                move.department_id = False
