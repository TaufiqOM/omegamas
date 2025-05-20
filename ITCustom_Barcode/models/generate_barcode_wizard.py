# omegamas/ITCustom_Barcode/models/generate_barcode_wizard.py
from odoo import models, fields, api
import base64
from io import BytesIO
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class GenerateBarcodeWizard(models.TransientModel):
    _name = 'generate.barcode.wizard'
    _description = 'Wizard Generate Barcode'
    
    def generate_barcode_pdf(self, jumlah=1):
        self.ensure_one()
        kode_utama = "200000"
        subkode_ids = []
        for i in range(1, jumlah + 1):
            subkode = f"{kode_utama}-{str(i).zfill(4)}-{str(jumlah).zfill(4)}"
            record = self.env['barcode.produksi.subkode'].create({
                'name': subkode,
                'produk_id': self.id,
                'kode': kode_utama,
                'create_date': fields.Date.context_today(self),
            })
            subkode_ids.append(record)

        # Generate PDF with QR codes (sama seperti kode sebelumnya)
        from io import BytesIO
        import base64
        import qrcode
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        pdf_buffer = BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=A4)
        x = 50
        y = 750
        for subkode in subkode_ids:
            qr = qrcode.make(subkode.name)
            qr_buffer = BytesIO()
            qr.save(qr_buffer)
            qr_buffer.seek(0)
            p.drawImage(qr_buffer, x, y, width=100, height=100)
            p.drawString(x + 120, y + 40, subkode.name)

            y -= 120
            if y < 100:
                p.showPage()
                y = 750
        p.save()
        pdf_buffer.seek(0)

        pdf_file = base64.b64encode(pdf_buffer.read())
        pdf_buffer.close()

        attachment = self.env['ir.attachment'].create({
            'name': f'Barcodes-{self.name}.pdf',
            'type': 'binary',
            'datas': pdf_file,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }
