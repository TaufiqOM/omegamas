from odoo import api, fields, models


class MrpProductionBackorder(models.TransientModel):
    _inherit = 'mrp.production.backorder'

    def action_backorder(self):
        # Panggil method original action_backorder
        res = super().action_backorder()

        for order in self.mrp_production_ids:
            date_start = order.date_start or fields.Date.today()
            year = date_start.year % 100  # Ambil dua digit terakhir tahun
            month = date_start.month
            day = date_start.day

            picking_type_code = order.picking_type_id.sequence_code or 'XXX'

            # Cari sequence terakhir untuk tanggal yang sama
            existing_orders = self.env['mrp.production'].search([
                ('name', 'like', f"{picking_type_code} {year:02d}/{month:02d}/{day:02d}-%")
            ], order="name desc", limit=1)

            if existing_orders:
                last_sequence = int(existing_orders.name.split('-')[-1]) + 1
            else:
                last_sequence = 1

            # Format nomor sequence
            new_name = f"{picking_type_code} {year:02d}/{month:02d}/{day:02d}-{last_sequence:03d}"

            order.name = new_name  # Update nama MO dengan format baru

        return res
