from odoo import models, fields, api
from datetime import datetime, timedelta

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    name = fields.Char(string="Reference", default="Draft")  # Bisa diedit, default "Draft"

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') == 'Draft':
            vals['name'] = self._generate_draft_name()
        return super(StockPicking, self).create(vals)

    def _generate_draft_name(self):
        """ Generate nama Draft unik jika sudah ada "Draft - 1", maka menjadi "Draft - 2", dst. """
        existing_drafts = self.search([('name', '=like', 'Draft - %')], order='name desc', limit=1)
        if existing_drafts:
            last_number = existing_drafts.name.replace('Draft - ', '').strip()
            new_number = int(last_number) + 1 if last_number.isdigit() else 1
            return f"Draft - {new_number}"
        return "Draft - 1"

    @api.model
    def _generate_sequence_number(self, schedule_date):
        """Membuat nomor urut unik berdasarkan tahun dan bulan dari schedule_date dalam zona waktu WIB (UTC+7)"""
        if not schedule_date:
            schedule_date = fields.Datetime.now()

        # Konversi UTC ke WIB (UTC+7)
        date_obj = fields.Datetime.from_string(schedule_date) + timedelta(hours=7)
        year = date_obj.strftime("%y")
        month = date_obj.strftime("%m")

        # Mencari nomor urut terakhir dalam bulan yang sama
        domain = [('name', 'like', f'STRG/TTB {year}/{month}/%')]
        last_picking = self.search(domain, order="name desc", limit=1)

        if last_picking and last_picking.name:
            try:
                last_number = int(last_picking.name.split("/")[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0

        return f"STRG/TTB {year}/{month}/{last_number + 1:03d}"

    def button_validate(self):
        """Override validasi untuk selalu mengubah name sesuai format saat divalidasi"""
        for picking in self:
            picking.name = self._generate_sequence_number(picking.scheduled_date)

        return super(StockPicking, self).button_validate()
