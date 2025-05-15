from odoo import fields, models, api


class SaleBlanketOrderLine (models.Model):
    _inherit = 'sale.blanket.order.line'
    _description = 'Add field sales needed'

    info_to_buyer = fields.Text(
        string="Info to Buyer",
        copy=False,
        help='Information to buyer',
    )
    info_to_production = fields.Text(
        string="Info to Production",
        help="Information provided to the production team."
    )
    type_product = fields.Selection(
        selection=[
            ('int', 'INT'),
            ('ext', 'EXT'),
            ('hdl', 'HDL'),
        ],
        string="Type",
        store=True,
        help="Type Proction",
        default='int'
    )

    supp_order = fields.Many2one(
        'supp.order',
        string="Supp",
    )

    external_id = fields.Many2one(
        'sale.id.external',
        string="External ID",
        help="Pilih ID External untuk produk ini",
    )

    sec_price = fields.Float(
        string="OM Price",
        help="OM Price"
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


