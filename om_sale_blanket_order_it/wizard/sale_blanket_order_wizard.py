from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta


class SaleBlanketOrderWizard(models.TransientModel):
    _inherit = 'sale.blanket.order.wizard'
    _description = 'Create BackDate '

    date_create_sale_order = fields.Date(
        string="Create SO",
        help="Tanggal pembuatan Sales Order",
        copy=False,
        required=True
    )

    @api.model
    def _get_next_sequence(self, year, month):
        """Menghasilkan nomor urut (3 digit) berdasarkan tahun & bulan"""
        last_request = self.env["sale.order"].search([
            ("name", "like", f"SO {year}/{month}/%"),
        ], order="name desc", limit=1)

        if last_request:
            last_number = int(last_request.name[-3:])  # Ambil angka terakhir
            return f"{last_number + 1:03d}"  # Tambah 1 dengan format 3 digit
        else:
            return "001"  # Mulai dari 001 jika belum ada

    def create_sale_order(self):
        """Membuat Sales Order dari Wizard dan mengisi field 'name' di sale.order"""
        res = super().create_sale_order()  # Memanggil fungsi bawaan

        for record in self:
            if not record.date_create_sale_order:
                raise exceptions.ValidationError("Tanggal 'Create SO' harus diisi!")

            # 🔍 Ambil Blanket Order dari wizard line
            wizard_line = self.env["sale.blanket.order.wizard.line"].search([
                ("wizard_id", "=", record.id)
            ], limit=1)

            if not wizard_line or not wizard_line.order_id:
                raise exceptions.ValidationError("Blanket Order tidak ditemukan di Wizard!")

            blanket_order = wizard_line.order_id  # Ambil Blanket Order

            # 🔥 Perbaikan: Gunakan `record.date_create_sale_order`
            date_bo_wib = datetime.combine(record.date_create_sale_order, datetime.min.time()) + timedelta(hours=7)

            year = date_bo_wib.strftime("%y")  # Format YY
            month = date_bo_wib.strftime("%m")  # Format MM
            sequence = self._get_next_sequence(year, month)

            new_name = f"SO {year}/{month}/{sequence}"

            # 🔍 Perbaikan: Cari SO berdasarkan 'origin' dari Blanket Order
            sale_order = self.env["sale.order"].search([
                ("origin", "=", blanket_order.name)  # Ambil nama Blanket Order
            ], order="id desc", limit=1)

            if sale_order:
                sale_order.write({
                    "name": new_name,  # Update nama SO
                    "date_order": record.date_create_sale_order  # Set tanggal order
                })
            else:
                raise exceptions.ValidationError(f"Gagal menemukan Sales Order dengan origin {blanket_order.name}")

        return res
