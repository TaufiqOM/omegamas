from odoo import models, fields, api
import io
import base64
from odoo.tools import pycompat

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    def _get_export_data(self, fields):
        # Original export data preparation
        data = super(HrPayslip, self)._get_export_data(fields)
        
        # Convert to list if not already
        if not isinstance(data, list):
            data = list(data)
        
        # Add 5 empty rows at the beginning
        header_rows = 5
        empty_row = {field: '' for field in fields}
        modified_data = [empty_row.copy() for _ in range(header_rows)] + data
        
        return modified_data
    
    def _export(self, fields):
        # Override the export method to modify the output
        import_compatible = self._context.get('import_compatible_export', False)
        
        # Get the modified data
        data = self._get_export_data(fields)
        
        # Generate CSV
        f = io.BytesIO()
        writer = pycompat.csv_writer(f, quoting=1)
        
        # Write header if not import compatible
        if not import_compatible:
            writer.writerow(fields)
        
        # Write data rows
        for row in data:
            writer.writerow([row.get(field, '') for field in fields])
        
        # Prepare file for download
        f.seek(0)
        file_data = f.read()
        f.close()
        
        # Encode and return
        b64 = base64.b64encode(file_data)
        filename = self._context.get('export_filename', 'export')
        extension = self._context.get('export_file_extension', 'csv')
        return {
            'file': b64,
            'filename': '%s.%s' % (filename, extension),
            'file_type': extension,
        }