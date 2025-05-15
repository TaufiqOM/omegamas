from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Custom sales order line'

    blanket_order_line = fields.Many2one(
        'sale.blanket.order.line',
        string='Blanket Line Reference'
    )

    info_to_buyer = fields.Text(
        related='blanket_order_line.info_to_buyer',
        store=True,
        readonly=False,
    )

    info_to_production = fields.Text(
        related='blanket_order_line.info_to_production',
        store=True,
        readonly=False,
    )

    analytic_precision = fields.Integer(default=2)

    analytic_distribution = fields.Json(
        string="Proyek",
        related='blanket_order_line.analytic_distribution',
        store=True,
        readonly=False,
    )

    type_product = fields.Selection(
        related="blanket_order_line.type_product",
        string="Type",
        store=True,
        help="Type Proction",
    )

    supp_order = fields.Many2one(
        related="blanket_order_line.supp_order",
        string="Supp",
        store=True,
    )

    external_id = fields.Many2one(
        related="blanket_order_line.external_id",
        string="External ID",
        help="Pilih ID External untuk produk ini",
        store=True,
    )

    sec_price = fields.Float(
        related="blanket_order_line.sec_price",
        string="OM Price",
        help="OM Price",
        store=True,
    )

    analytic_names = fields.Char(compute='_compute_analytic_names', string='Analytic Names')

    def _compute_analytic_names(self):
        for line in self:
            if line.analytic_distribution:
                ids = [int(i) for i in line.analytic_distribution.keys()]
                names = self.env['account.analytic.account'].browse(ids).mapped('name')
                line.analytic_names = ', '.join(names)
            else:
                line.analytic_names = ''
