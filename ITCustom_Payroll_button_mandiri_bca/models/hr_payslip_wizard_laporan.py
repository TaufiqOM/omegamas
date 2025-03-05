from odoo import models, fields, api

class HrPayslipWizard(models.TransientModel):
    _name = 'hr.payslip.wizard.laporan'
    _description = 'Wizard Export Laporan'

    export_date = fields.Date(string="Tanggal Pembayaran", required=True, default=fields.Date.context_today)

    def action_confirm(self):
        """
        Method yang dijalankan saat tombol Export di wizard ditekan.
        Menyimpan tanggal yang dipilih ke context dan memanggil method export_to_laporan.
        """
        active_ids = self.env.context.get('active_ids', [])
        payslips = self.env['hr.payslip'].browse(active_ids)

        # Simpan export_date ke context agar bisa digunakan di method export_to_laporan
        self.env.context = dict(self.env.context, export_date=self.export_date)

        # Panggil method export_to_laporan untuk mengekspor data ke Excel
        return payslips.export_to_laporan(self.export_date)