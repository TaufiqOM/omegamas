from odoo import fields, models, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Field  #
    confirmation_date_order = fields.Date(
        string='Confirmation Date',
        copy=False,
        help="Confirmation Date"
    )

    due_date_order = fields.Date(
        string="Due Date",
        copy=False,
        help="Due Date"
    )

    due_date_update_order = fields.Date(
        string="Due Date Update",
        copy=False,
        tracking=True
    )

    count_revisi_order = fields.Integer(
        string="Revisi Order",
        copy=False,
        tracking=True
    )

    date_revisi_order = fields.Date(
        string="Date Revisi Order",
        copy=False,
        tracking=True
    )

    is_closed = fields.Boolean('Closed PO', default=False, copy=False)
    closed_badge = fields.Char(compute='_compute_closed_badge', string='Closed Badge', store=False)

    def button_close(self):
        for order in self:
            if order.delivery_status != 'full':
                raise UserError("Delivery status harus 'full' sebelum bisa ditutup.")
            if order.state != 'sale':
                raise UserError("Order harus berada dalam status 'Sale Order' untuk bisa ditutup.")
            if order.invoice_status != 'invoiced':
                raise UserError("Order harus sudah sepenuhnya difakturkan (Full Invoiced) sebelum bisa ditutup.")

            order.write({
                'is_closed': True,
                'locked': True,
            })

    def _compute_closed_badge(self):
        for order in self:
            order.closed_badge = 'CLOSED' if order.is_closed else ''

     # Total Order Qty
    total_order_qty = fields.Float(
        string="Total Order",
        compute="_compute_total_qty_order"
    )

    @api.depends('order_line.product_uom_qty')
    def _compute_total_qty_order(self):
        for order in self:
            order.total_order_qty = sum(order.order_line.mapped('product_uom_qty'))

    # Total Delivery Qty
    total_delivery_qty = fields.Float(
        string="Total Delivery",
        compute="_compute_total_qty_delivery",
    )

    @api.depends('order_line.qty_delivered')
    def _compute_total_qty_delivery(self):
        for delivery in self:
            delivery.total_delivery_qty = sum(delivery.order_line.mapped('qty_delivered'))



