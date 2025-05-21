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
        from reportlab.lib.utils import ImageReader
        import qrcode
        import base64
        import tempfile
        from io import BytesIO

        STICKER_WIDTH = 10 * cm
        STICKER_HEIGHT = 15 * cm

        pdf_buffer = BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=(STICKER_WIDTH, STICKER_HEIGHT))

        x = 0.5 * cm
        y = STICKER_HEIGHT - 0.5 * cm
        header_height = 1.8 * cm
        logo_width = 1.8 * cm
        code_width = 4.2 * cm
        date_width = 2.5 * cm

        company = self.env.company
        logo_img = None
        if company.logo:
            logo_stream = BytesIO(base64.b64decode(company.logo))
            logo_img = ImageReader(logo_stream)

        for rec in self:
            # Ambil informasi
            kode_produk = rec.produk_id.default_code or "NoCode"
            sale_order = self.env['sale.order'].browse(rec.order_id.id)
            if sale_order.due_date_order:
                due_date_str = sale_order.due_date_order.strftime('%b%y')
            else:
                due_date_str = "NoDate"

            # Gambar border header
            p.rect(x, y - header_height, logo_width, header_height)
            p.rect(x + logo_width, y - header_height, code_width, header_height)
            p.rect(x + logo_width + code_width, y - header_height, date_width, header_height)

            # Logo perusahaan
            if logo_img:
                p.drawImage(logo_img, x + 0.15 * cm, y - header_height + 0.15 * cm, width=1.5 * cm, height=1.5 * cm, preserveAspectRatio=True)

            # Set font
            p.setFont("Helvetica-Bold", 10)

            # Kode produk di tengah
            center_x_code = x + logo_width + code_width / 2
            center_y = y - header_height / 2 - 3  # sedikit geser ke bawah
            p.drawCentredString(center_x_code, center_y, kode_produk)

            # Due date di tengah
            center_x_date = x + logo_width + code_width + date_width / 2
            p.drawCentredString(center_x_date, center_y, due_date_str)

            # QR Code
            qr = qrcode.make(rec.name)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                qr.save(tmp.name)
                p.drawImage(tmp.name, x, y - header_height - 4 * cm, width=4 * cm, height=4 * cm)

            # Nama barcode
            p.setFont("Helvetica", 10)
            p.drawString(x + 4.5 * cm, y - header_height - 2 * cm, rec.name)

            p.showPage()

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
