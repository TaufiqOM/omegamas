from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    product_id = fields.Many2one('product.product', string="Product", compute="_compute_product")

    @api.depends('move_ids')
    def _compute_product(self):
        for record in self:
            if record.move_ids:
                stock_move = record.move_ids[0]  # Ambil move pertama
                record.product_id = stock_move.product_id.id
            else:
                record.product_id = False
