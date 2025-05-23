# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_Payroll_button_mandiri_bca/models/hr_payslip_wizard_laporan.py
from odoo import models, fields, api

class HrPayslipWizard(models.TransientModel):
    _name = 'hr.payslip.wizard.laporan'
    _description = 'Wizard Export Laporan'

    export_date = fields.Date(string="Tanggal Pembayaran", required=True, default=fields.Date.context_today)
    export_type = fields.Selection([
        ('excel', 'Excel'),
        ('pdf', 'PDF')
    ], string="Jenis File", required=True, default='excel')

    def action_confirm(self):
        active_ids = self.env.context.get('active_ids', [])
        payslips = self.env['hr.payslip'].browse(active_ids)

        export_date = self.export_date
        export_type = self.export_type

        if export_type == 'excel':
            return payslips.export_to_laporan(export_date)
        elif export_type == 'pdf':
            return payslips.export_to_laporan_pdf(export_date)  # <-- kamu bisa buat method ini nanti
        

