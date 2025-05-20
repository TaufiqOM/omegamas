# models/barcode_subkode.py
import tempfile
from odoo import models, fields, api
import base64
from io import BytesIO
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class BarcodeProduksiSubkode(models.Model):
    _name = 'barcode.produksi.subkode'
    _description = 'Sub Kode Barcode Produksi'
    _order = 'id desc'

    name = fields.Char("Kode Barcode", required=True)
    order_id = fields.Many2one('sale.order', string='Nomor Penjualan')
    produk_id = fields.Many2one('product.template', string="Produk", required=True)
    produksi_id = fields.Many2one('barcode.produksi', string="Barcode Produksi", ondelete='cascade')
    kode = fields.Char(string="Kode Utama", required=True)
    create_date = fields.Date(string="Tanggal Generate", required=True, readonly=True)
    
    def action_generate_barcode_direct(self):
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        import qrcode

        # Ukuran stiker: 10cm x 15cm
        STICKER_WIDTH = 10 * cm
        STICKER_HEIGHT = 15 * cm

        pdf_buffer = BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=(STICKER_WIDTH, STICKER_HEIGHT))

        x = 1 * cm  # jarak dari kiri
        y = STICKER_HEIGHT - 5 * cm  # posisi awal dari atas

        for rec in self:
            qr = qrcode.make(rec.name)

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                qr.save(tmp.name)
                p.drawImage(tmp.name, x, y, width=4 * cm, height=4 * cm)

            # Tambahkan teks kode barcode
            p.setFont("Helvetica", 10)
            p.drawString(x + 4.5 * cm, y + 2 * cm, rec.name)

            p.showPage()  # Buat halaman baru untuk setiap barcode

        p.save()
        pdf_buffer.seek(0)

        pdf_file = base64.b64encode(pdf_buffer.read())
        pdf_buffer.close()

        attachment = self.env['ir.attachment'].create({
            'name': 'Barcode_QRCode.pdf',
            'type': 'binary',
            'datas': pdf_file,
            'res_model': self._name,
            'res_id': self.ids[0] if self else None,
            'mimetype': 'application/pdf',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }
