from odoo import fields, models, api


class IdExternal(models.Model):
    _name = 'sale.id.external'
    _description = 'Sale Id External'

    name = fields.Char(
        string="Name",
        copy=False,
        required=True,
        placeholder="Nama - Buyer - Product"
    )

    buyer = fields.Many2one(
        'res.partner',
        string="Buyer",
        copy=False,
        required=True,
        domain=[('category_id', 'in', [1, 2])]
    )

    product = fields.Many2one(
        'product.template',
        string="Product",
        copy=False,
        required=True,
        domain=[('categ_id', '=', 69)]
    )

    primary_id = fields.Char(
        string="Primary ID",
        copy=False,
        required=True,
    )
    secondary_id = fields.Char(
        string="Secondary ID",
        copy=False,
    )


