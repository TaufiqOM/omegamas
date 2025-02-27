from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    move_id = fields.Many2one('stock.move', string="Stock Move", compute="_compute_testing")

    @api.depends('move_ids')
    def _compute_testing(self):
        for record in self:
            if record.move_ids:
                stock_move = self.env['stock.move'].search([('account_id', '=', record.move_ids[0].id)], limit=1)
                if stock_move:
                    record.move_id = stock_move.id
                else:
                    record.move_id = False
            else:
                record.move_id = False


class StockMove(models.Model):
    _inherit = 'stock.move'

    account_id = fields.Many2one('account.account', string="Account")
