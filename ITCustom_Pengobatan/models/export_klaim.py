import io
import xlsxwriter
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.http import content_disposition
from odoo.tools import date_utils
import base64
from datetime import datetime

class PengobatanKlaim(models.Model):
    _inherit = 'pengobatan.klaim'

    def export_klaim_action(self, active_ids):
        # Ambil data yang dipilih
        klaims = self.browse(active_ids)
        
        if not klaims:
            raise UserError("Tidak ada data yang dipilih untuk diekspor.")
        
        # Buat file Excel dalam memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Data Klaim')
        
        # Format untuk styling
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'font_size': 12
        })
        
        data_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'font_size': 11
        })
        
        date_format = workbook.add_format({
            'border': 1,
            'num_format': 'dd/mm/yyyy',
            'font_size': 11
        })
        
        currency_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0.00',
            'font_size': 11
        })
        
        # Header kolom
        headers = [
            {'label': 'No', 'width': 5},
            {'label': 'Nomor Klaim', 'width': 20},
            {'label': 'Nomor Karyawan', 'width': 30},
            {'label': 'Nama Karyawan', 'width': 30},
            {'label': 'Tanggal Klaim', 'width': 15},
            {'label': 'Nominal', 'width': 15},
            {'label': 'Keterangan', 'width': 40}
        ]
        
        # Tulis header
        for col, header in enumerate(headers):
            worksheet.write(0, col, header['label'], header_format)
            worksheet.set_column(col, col, header['width'])
        
        # Tulis data
        for row, klaim in enumerate(klaims, start=1):
            # No urut
            worksheet.write(row, 0, row, data_format)
            
            # Nomor Klaim
            worksheet.write(row, 1, klaim.name or '', data_format)
            
            # Nomor Karyawan
            employee_no = klaim.employee_id.barcode or ''
            worksheet.write(row, 2, employee_no, data_format)
            
            # Nama Karyawan
            employee_name = klaim.employee_id.name or ''
            worksheet.write(row, 3, employee_name, data_format)
            
            # Tanggal Klaim
            worksheet.write(row, 4, klaim.tanggal_klaim, date_format)
            
            # Nominal
            worksheet.write(row, 5, klaim.nominal or 0, currency_format)
            
            # Keterangan
            worksheet.write(row, 6, klaim.keterangan or '', data_format)
        
        # Total nominal
        total_row = len(klaims) + 1
        worksheet.write(total_row, 4, 'TOTAL:', header_format)
        worksheet.write_formula(
            total_row, 5,
            f'=SUM(E2:E{total_row})',
            currency_format
        )
        
        # Freeze header row
        worksheet.freeze_panes(1, 0)
        
        # Tutup workbook
        workbook.close()
        output.seek(0)
        
        # Generate nama file
        today = fields.Date.today()
        filename = f"Export_Klaim_{today.strftime('%Y%m%d')}.xlsx"
        
        # Buat attachment
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': base64.b64encode(output.getvalue()),
            'res_model': 'pengobatan.klaim',
            'type': 'binary',
        })
        
        # Return action untuk download
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }