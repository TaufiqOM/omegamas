from odoo import fields, models, api, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_next_sequence(self, prefix, year, month):
        """Menghasilkan nomor urut unik (3 digit) berdasarkan tahun & bulan"""
        sequence = 1  # Mulai dari 001
        while True:
            new_sequence = f"{sequence:03d}"  # Format 3 digit (001, 002, ...)
            new_name = f"{prefix} {year}/{month}/{new_sequence}"

            if not self.search([("name", "=", new_name)]):
                return new_sequence  # Return jika belum ada di database

            sequence += 1  # Jika sudah ada, coba nomor berikutnya

    def button_validate(self):
        """Mengubah name berdasarkan picking_type_code saat tombol Validate ditekan"""
        for record in self:
            if not record.scheduled_date:
                raise exceptions.ValidationError("Tanggal 'Scheduled Date' harus diisi!")

            # Gunakan timezone Odoo untuk memastikan waktu sesuai dengan lokal user
            date_scheduled_wib = fields.Datetime.context_timestamp(record, record.scheduled_date)

            year = date_scheduled_wib.strftime("%y")  # Format YY
            month = date_scheduled_wib.strftime("%m")  # Format MM

            # Tentukan prefix berdasarkan picking_type_code
            picking_prefix = {
                "incoming": "STRG/TTB",
                "outgoing": "STRG/DO",
                "internal": "STRG/INT",
            }.get(record.picking_type_code, "STRG/UNK")  # Default jika tidak ada di daftar

            # Dapatkan nomor urut yang unik
            sequence = self._get_next_sequence(picking_prefix, year, month)
            new_name = f"{picking_prefix} {year}/{month}/{sequence}"

            record.sudo().write({"name": new_name})  # Update name dengan sudo agar tidak ada permission issue

        return super().button_validate()

    # Total Qty Delivery
    total_delivery_qty = fields.Float(string="Total Delivered", compute="_compute_total_delivery_qty", store=True)

    @api.depends('move_ids_without_package.quantity')
    def _compute_total_delivery_qty(self):
        for picking in self:
            picking.total_delivery_qty = sum(picking.move_ids_without_package.mapped('quantity'))

    # Total Qty Sales Order
    total_sales_order_qty = fields.Float(string="Total Delivered", compute="_compute_total_sales_order_qty", store=True)

    @api.depends('move_ids_without_package.product_uom_qty')
    def _compute_total_sales_order_qty(self):
        for picking in self:
            picking.total_sales_order_qty = sum(picking.move_ids_without_package.mapped('product_uom_qty'))

