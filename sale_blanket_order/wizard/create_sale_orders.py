# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class BlanketOrderWizard(models.TransientModel):
    _name = "sale.blanket.order.wizard"
    _description = "Blanket order wizard"

    @api.model
    def _default_order(self):
        # in case the cron hasn't run
        self.env["sale.blanket.order"].expire_orders()
        if not self.env.context.get("active_id"):
            return False
        blanket_order_line = self.env["sale.blanket.order.line"].search(
            [("id", "=", self.env.context["active_id"])], limit=1)
        blanket_order = self.env["sale.blanket.order"].search(
            [("id", "=", blanket_order_line.order_id.id)], limit=1
        )
        if blanket_order.state == "expired":
            raise UserError(
                _("You can't create a sale order from " "an expired blanket order!")
            )
        return blanket_order

    @api.model
    def _check_valid_blanket_order_line(self, bo_lines):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        company_id = False

        if all(
            float_is_zero(line.remaining_uom_qty, precision_digits=precision)
            for line in bo_lines
        ):
            raise UserError(_("The sale has already been completed."))

        for line in bo_lines:
            if line.order_id.state != "open":
                raise UserError(
                    _("Sale Blanket Order %s is not open") % line.order_id.name
                )
            line_company_id = line.company_id and line.company_id.id or False
            if company_id is not False and line_company_id != company_id:
                raise UserError(_("You have to select lines " "from the same company."))
            else:
                company_id = line_company_id

    @api.model
    def _default_lines(self):
        blanket_order_line_obj = self.env["sale.blanket.order.line"]
        blanket_order_line_ids = self.env.context.get("active_ids", False)
        active_model = self.env.context.get("active_model", False)

        if active_model == "sale.blanket.order":
            bo_lines = self._default_order().line_ids
        else:
            bo_lines = blanket_order_line_obj.browse(blanket_order_line_ids)

        self._check_valid_blanket_order_line(bo_lines)

        lines = [
            (
                0,
                0,
                {
                    "blanket_line_id": bol.id,
                    "product_id": bol.product_id.id,
                    "date_schedule": bol.date_schedule,
                    "remaining_uom_qty": bol.remaining_uom_qty,
                    "price_unit": bol.price_unit,
                    "product_uom": bol.product_uom,
                    "qty": bol.remaining_uom_qty,
                    "partner_id": bol.partner_id,
                },
            )
            for bol in bo_lines.filtered(
                lambda bo_line: not bo_line.display_type
                and bo_line.remaining_uom_qty != 0.0
            )
        ]
        return lines

    blanket_order_id = fields.Many2one(
        comodel_name="sale.blanket.order",
        readonly=True,
        default=lambda self: self._default_order(),
    )
    sale_order_id = fields.Many2one(
        "sale.order", string="Purchase Order", domain=[("state", "=", "draft")]
    )
    line_ids = fields.One2many(
        "sale.blanket.order.wizard.line",
        "wizard_id",
        string="Lines",
        default=_default_lines,
    )
    dp_blanket = fields.Float(compute='_compute_dp_blanket', store=True)

    dp_order = fields.Float(
        string="Order Down Payment",
    )

    @api.depends('line_ids')
    def _compute_dp_blanket(self):
        if self.line_ids[0].blanket_line_id.order_id.dp_sisa == 0:
            self.dp_blanket = self.line_ids[0].blanket_line_id.order_id.down_payment
        else:
            self.dp_blanket = self.line_ids[0].blanket_line_id.order_id.dp_sisa


    @api.onchange('dp_order', 'dp_blanket')
    def onchange_down_payment(self):
        if self.dp_order > self.dp_blanket:
            raise UserError("Order Down Payment Exceeding Down Payment")

    def _prepare_so_line_vals(self, line):
        return {
            "product_id": line.product_id.id,
            "name": line.product_id.name,
            "product_uom": line.product_uom.id,
            "sequence": line.blanket_line_id.sequence,
            "price_unit": line.blanket_line_id.price_unit,
            "blanket_order_line": line.blanket_line_id.id,
            "product_uom_qty": line.qty,
            "tax_id": [(6, 0, line.taxes_id.ids)],
        }

    def _prepare_so_vals(
        self,
        customer,
        user_id,
        currency_id,
        pricelist_id,
        payment_term_id,
        order_lines_by_customer,
    ):
        return {
            "partner_id": customer,
            "origin": self.blanket_order_id.name,
            "user_id": user_id,
            "currency_id": currency_id,
            "pricelist_id": pricelist_id,
            "payment_term_id": payment_term_id,
            "order_line": order_lines_by_customer[customer],
            "analytic_account_id": self.blanket_order_id.analytic_account_id.id,
        }

    def create_sale_order(self):
        order_lines_by_customer = defaultdict(list)
        currency_id = 0
        pricelist_id = 0
        user_id = 0
        payment_term_id = 0
        dp_order = self.dp_order
        # for rec in self.line_ids.order_id:
        #     print('rec', rec.line_ids.order_id)
        #     rec.dp_order += self.dp_order
        #     rec.dp_sisa = self.dp_blanket - self.dp_order
        for rec in self.line_ids.order_id:
            blanket = self.env['sale.blanket.order'].search([('id', '=', self.blanket_order_id.id)])
            if blanket:
                # print('rec line', rec.line_ids.order_id)
                # print(blanket)
                # total_dp_order = sum(
                #     o.dp_order for o in self.search([('id', '=', self.blanket_order_id.id)])
                # )
                rec.dp_order += self.dp_order
                rec.dp_sisa = rec.down_payment - rec.dp_order
                # print('dp', rec.down_payment)
                # print(rec.dp_order)

                for line in rec.line_ids:
                    line.dp_order += self.dp_order
                    line.dp_sisa = rec.down_payment - rec.dp_order

                # blanket.write({
                #     'dp_order': rec.dp_order
                # })

            else:
                rec.dp_order = 0.0
                rec.dp_sisa = 0.0

                for line in rec.line_ids:
                    line.dp_order = 0.0
                    line.dp_sisa = 0.0

        for line in self.line_ids.filtered(lambda line: line.qty != 0.0):
            if line.qty > line.remaining_uom_qty:
                raise UserError(_("You can't order more than the remaining quantities"))
            vals = self._prepare_so_line_vals(line)
            order_lines_by_customer[line.partner_id.id].append((0, 0, vals))

            if currency_id == 0:
                currency_id = line.blanket_line_id.order_id.currency_id.id
            elif currency_id != line.blanket_line_id.order_id.currency_id.id:
                currency_id = False

            if pricelist_id == 0:
                pricelist_id = line.blanket_line_id.pricelist_id.id
            elif pricelist_id != line.blanket_line_id.pricelist_id.id:
                pricelist_id = False

            if user_id == 0:
                user_id = line.blanket_line_id.user_id.id
            elif user_id != line.blanket_line_id.user_id.id:
                user_id = False

            if payment_term_id == 0:
                payment_term_id = line.blanket_line_id.payment_term_id.id
            elif payment_term_id != line.blanket_line_id.payment_term_id.id:
                payment_term_id = False

        if not order_lines_by_customer:
            raise UserError(_("An order can't be empty"))

        if not currency_id:
            raise UserError(
                _(
                    "Can not create Sale Order from Blanket "
                    "Order lines with different currencies"
                )
            )

        res = []
        for customer in order_lines_by_customer:
            order_vals = self._prepare_so_vals(
                customer,
                user_id,
                currency_id,
                pricelist_id,
                payment_term_id,
                order_lines_by_customer,
            )
            sale_order = self.env["sale.order"].create(order_vals)
            if not sale_order.dp_blanket:
                obj = {
                # 'dp_order': dp_order,
                # 'dp_sisa': self.dp_blanket - dp_order,
                'dp_blanket': dp_order
                }
                sale_order.write(obj)
        
            # sale_order.write({
            #     'dp_order': dp_order,
            #     'dp_sisa': self.dp_blanket - dp_order
            # })
            # sale_order.write(obj)
            res.append(sale_order.id)
        return {
            "domain": [("id", "in", res)],
            "name": _("Sales Orders"),
            "view_type": "form",
            "view_mode": "list,form",
            "res_model": "sale.order",
            "context": {"from_sale_order": True},
            "type": "ir.actions.act_window",
        }


class BlanketOrderWizardLine(models.TransientModel):
    _name = "sale.blanket.order.wizard.line"
    _description = "Blanket order wizard line"

    wizard_id = fields.Many2one("sale.blanket.order.wizard")
    blanket_line_id = fields.Many2one("sale.blanket.order.line")
    product_id = fields.Many2one(
        "product.product", related="blanket_line_id.product_id", string="Product"
    )
    order_id = fields.Many2one(
        "sale.blanket.order", related="blanket_line_id.order_id", string="Blanket Order"
    )
    product_uom = fields.Many2one(
        "uom.uom", related="blanket_line_id.product_uom", string="Unit of Measure"
    )
    date_schedule = fields.Date(string="Scheduled Date")
    remaining_uom_qty = fields.Float(related="blanket_line_id.remaining_uom_qty")
    dp_blanket = fields.Float(related="blanket_line_id.dp_blanket")
    qty = fields.Float(string="Quantity to Order", required=True)
    price_unit = fields.Float(related="blanket_line_id.price_unit")
    currency_id = fields.Many2one("res.currency", related="blanket_line_id.currency_id")
    partner_id = fields.Many2one(
        "res.partner", related="blanket_line_id.partner_id", string="Vendor"
    )
    taxes_id = fields.Many2many("account.tax", related="blanket_line_id.taxes_id")
