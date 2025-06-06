# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    sale_manual_delivery = fields.Boolean(
        related="company_id.sale_manual_delivery", readonly=False
    )
