from odoo import models, fields, api
from datetime import timedelta

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    name = fields.Char(string="Reference", default="Draft")  # Bisa diedit, default "Draft"
    sale_id = fields.Many2one('sale.order', string="Sale Order")  # Relasi ke sale.order jika ada

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') == 'Draft':
            vals['name'] = self._generate_draft_name()
        return super().create(vals)

    def _generate_draft_name(self):
        """ Generate nama Draft unik jika sudah ada "Draft - 1", maka menjadi "Draft - 2", dst. """
        existing_drafts = self.search([('name', '=like', 'Draft - %')], order='name desc', limit=1)
        if existing_drafts:
            last_number = existing_drafts.name.replace('Draft - ', '').strip()
            new_number = int(last_number) + 1 if last_number.isdigit() else 1
            return f"Draft - {new_number}"
        return "Draft - 1"

    @api.model
    def _generate_sequence_number(self, picking):
        """Membuat nomor urut unik berdasarkan model asal (`sale.order` atau tidak) dalam zona waktu WIB (UTC+7)"""
        schedule_date = picking.scheduled_date or picking.date_done or fields.Datetime.now()

        # Konversi UTC ke WIB (UTC+7)
        date_obj = fields.Datetime.from_string(schedule_date) + timedelta(hours=7)
        year = date_obj.strftime("%y")
        month = date_obj.strftime("%m")

        # Tentukan prefix berdasarkan asal dokumen
        prefix = "STRG/DO" if picking.sale_id else "STRG/TTB"

        # Mencari nomor urut terakhir dalam bulan yang sama dengan format yang sesuai
        domain = [('name', 'like', f'{prefix} {year}/{month}/%')]
        last_picking = self.search(domain, order="name desc", limit=1)

        last_number = 0
        if last_picking and last_picking.name:
            parts = last_picking.name.split("/")
            try:
                last_number = int(parts[-1])
            except ValueError:
                last_number = 0

        return f"{prefix} {year}/{month}/{last_number + 1:03d}"

    def button_validate(self):
        """Override validasi untuk selalu mengubah name sesuai format saat divalidasi"""
        for picking in self:
            picking.name = self._generate_sequence_number(picking)

        return super().button_validate()
