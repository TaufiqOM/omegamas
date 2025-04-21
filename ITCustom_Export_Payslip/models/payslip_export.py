from odoo import models, fields, api
import io
import base64
import csv

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    def _get_export_data(self, fields):
        # Get original data
        data = super(HrPayslip, self)._get_export_data(fields)
        
        # Convert to list if not already
        if not isinstance(data, list):
            data = list(data)
        
        return data
    
    def _export(self, fields):
        # Get the data
        data = self._get_export_data(fields)
        
        # Create file in memory
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        
        # Write 5 empty rows first
        for _ in range(5):
            writer.writerow([''] * len(fields))
        
        # Write header if not import compatible
        if not self._context.get('import_compatible_export', False):
            writer.writerow(fields)
        
        # Write data rows
        for row in data:
            writer.writerow([row.get(field, '') for field in fields])
        
        # Prepare file for download
        output.seek(0)
        file_data = output.read().encode('utf-8')
        output.close()
        
        # Encode and return
        b64 = base64.b64encode(file_data)
        filename = self._context.get('export_filename', 'export')
        extension = self._context.get('export_file_extension', 'csv')
        return {
            'file': b64,
            'filename': f'{filename}.{extension}',
            'file_type': extension,
        }