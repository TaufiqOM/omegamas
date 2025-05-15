from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    height = fields.Float(
        string="Height"
    )

    width = fields.Float(
        string="Width"
    )

    depth = fields.Float(
        string="Depth"
    )

    external_id = fields.One2many(
        'sale.id.external',
        'product',
        string="External ID",
        copy=False,
    )


