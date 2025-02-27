from odoo import models, fields, api
from datetime import datetime

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals_list):
        """ Override create untuk set nilai 'date_order' berdasarkan tanggal yang sudah disetting """
        if isinstance(vals_list, dict):
            vals_list = [vals_list]  # Pastikan format list

        for vals in vals_list:
            if not vals.get('date_order'):
                now = datetime.utcnow()
                vals['date_order'] = now.strftime('%Y-%m-%d %H:%M:%S')

        records = super().create(vals_list)
        return records

    def write(self, vals):
        """ Override write untuk memastikan date_order tetap menggunakan nilai yang sudah disetting """
        if 'date_order' not in vals:
            for order in self:
                if order.date_order:
                    vals['date_order'] = order.date_order.strftime('%Y-%m-%d %H:%M:%S')
        return super(SaleOrderInherit, self).write(vals)

    def action_confirm(self):
        """ Override action_confirm agar date_order tidak berubah saat konfirmasi """
        for order in self:
            original_date_order = order.date_order  # Simpan tanggal sebelum konfirmasi
            super(SaleOrderInherit, order).action_confirm()
            order.write({'date_order': original_date_order})  # Set ulang date_order agar tetap sama
        return True
