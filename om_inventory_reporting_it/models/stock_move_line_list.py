from odoo import fields, models, api


class StockMoveLineList(models.Model):
    _inherit = 'stock.move.line'


    depart_for_stock_move = fields.Many2one(
        'hr.department',
        string="Department",
        related='move_id.depart_per_prod',
        store=True,
        readonly=True
    )

    analytic_precision = fields.Integer(default=2)

    analytic_for_stock_move = fields.Json(
        string="Proyek",
        related='move_id.analytic_distribution',
        store=True,
        readonly=True,
    )

    note_per_stock_move_for_stock_move = fields.Html(
        string="Note",
        related="move_id.picking_id.note",
        store=True,
        readonly=True,
    )

    depart_mrp_production_for_stock_move = fields.Many2one(
        'hr.department',
        string='Department Manufacturing',
        related='move_id.production_id.department_id',
        store=True,
        readonly=True,
    )

    analytic_mrp_production_for_stock_move = fields.Many2one(
        string="Proyek Manufacturing",
        related="move_id.production_id.analytic_account_id",
        store=True,
        readonly=True,
    )

    note_mrp_production_for_stock_move = fields.Text(
        string="Note Manufacturing",
        related="move_id.production_id.log_note",
        store=True,
        readonly=True,
    )

