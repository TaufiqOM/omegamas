from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    show_valuation = fields.Boolean(string="Show Valuation", compute="_compute_show_valuation", store=True)

    @api.depends("move_finished_ids")
    def _compute_show_valuation(self):
        for record in self:
            record.show_valuation = bool(record.move_finished_ids)

    def action_view_stock_valuation_layers(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Stock Valuation Layers",
            "res_model": "stock.valuation.layer",
            "view_mode": "tree,form",
            "domain": [("production_id", "=", self.id)],
            "context": {"default_production_id": self.id},
        }
