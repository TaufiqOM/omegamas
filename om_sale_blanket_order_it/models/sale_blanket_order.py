from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta


class SaleBlanketOrder(models.Model):
    _inherit = 'sale.blanket.order'
    _description = 'Backdate Sale Blanket Order'

    date_create_blanket_order = fields.Date(
        string="Create BO",
        help="Date Create Blanket Order",
        copy=False,
        default=fields.Date.today
    )

    @api.model
    def _get_next_sequence(self, year, month):
        """Menghasilkan nomor urut (3 digit) berdasarkan tahun & bulan"""
        last_request = self.search([
            ("name", "like", f"BO {year}/{month}/%"),
        ], order="name desc", limit=1)

        if last_request:
            last_number = int(last_request.name[-3:])  # Ambil angka terakhir
            return f"{last_number + 1:03d}"  # Tambah 1 dengan format 3 digit
        else:
            return "001"  # Mulai dari 001 jika belum ada

    def action_confirm(self):
        """Mengubah name menjadi BO /YYYY/MM/XXX dengan tanggal dari Create BO"""
        res = super().action_confirm()  # Memanggil fungsi bawaan

        for record in self:
            if not record.date_create_blanket_order:
                raise exceptions.ValidationError("Tanggal 'Create BO' harus diisi!")

            # Konversi date_create_blanket_order ke datetime WIB (UTC+7)
            date_bo_wib = datetime.combine(record.date_create_blanket_order, datetime.min.time()) + timedelta(hours=7)

            year = date_bo_wib.strftime("%y")  # Format YY
            month = date_bo_wib.strftime("%m")  # Format MM
            sequence = self._get_next_sequence(year, month)

            new_name = f"BO {year}/{month}/{sequence}"

            # Validasi unik sebelum mengubah name
            if self.search([("name", "=", new_name)]):
                raise exceptions.ValidationError(f"Nama {new_name} sudah digunakan, mohon coba lagi.")

            record.name = new_name  # Update field name
        return res