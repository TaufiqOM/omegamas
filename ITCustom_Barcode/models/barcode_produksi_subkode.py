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
        from reportlab.lib import colors

        STICKER_WIDTH = 10 * cm
        STICKER_HEIGHT = 15 * cm
        MARGIN = 0.2 * cm

        pdf_buffer = BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=(STICKER_WIDTH, STICKER_HEIGHT))

        # Set up styles
        p.setFont("Helvetica", 8)
        small_font = 8
        medium_font = 9
        large_font = 10
        xlarge_font = 16

        company = self.env.company
        logo_img = None
        if company.logo:
            logo_stream = BytesIO(base64.b64decode(company.logo))
            logo_img = ImageReader(logo_stream)

        for rec in self:
            # Get information
            kode_produk = rec.produk_id.default_code or "NoCode"
            sale_order = rec.order_id
            product_name = rec.produk_id.name or "No Product Name"
            
            # Format dates
            create_date_str = rec.create_date.strftime('%d %b %y') if rec.create_date else "No Date"
            due_date_str = sale_order.due_date_order.strftime('%d %b %y') if sale_order and sale_order.due_date_order else "No Date"

            # Draw border around entire sticker
            p.rect(MARGIN, MARGIN, STICKER_WIDTH - 2*MARGIN, STICKER_HEIGHT - 2*MARGIN, stroke=1, fill=0)

            # Header Table
            header_table_y = STICKER_HEIGHT - MARGIN - 0.8*cm
            p.setStrokeColor(colors.black)
            p.setLineWidth(1)
            p.rect(MARGIN, header_table_y - 0.8*cm, STICKER_WIDTH - 2*MARGIN, 0.8*cm, stroke=1, fill=0)
            
            # Draw header table lines
            p.line(MARGIN + (STICKER_WIDTH - 2*MARGIN)/3, header_table_y, 
                MARGIN + (STICKER_WIDTH - 2*MARGIN)/3, header_table_y - 0.8*cm)
            p.line(MARGIN + 2*(STICKER_WIDTH - 2*MARGIN)/3, header_table_y, 
                MARGIN + 2*(STICKER_WIDTH - 2*MARGIN)/3, header_table_y - 0.8*cm)
            
            # Header text
            p.setFont("Helvetica-Bold", medium_font)
            p.drawString(MARGIN + 0.2*cm, header_table_y - 0.5*cm, "OM")
            p.drawCentredString(MARGIN + (STICKER_WIDTH - 2*MARGIN)/2, header_table_y - 0.5*cm, "4444")
            p.drawRightString(STICKER_WIDTH - MARGIN - 0.2*cm, header_table_y - 0.5*cm, "Date")

            # Description & QR Table
            desc_qr_y = header_table_y - 0.8*cm - MARGIN
            desc_qr_height = 1.5*cm
            p.rect(MARGIN, desc_qr_y - desc_qr_height, STICKER_WIDTH - 2*MARGIN, desc_qr_height, stroke=1, fill=0)
            
            # Vertical line for QR
            qr_width = 1.5*cm
            p.line(STICKER_WIDTH - MARGIN - qr_width, desc_qr_y, 
                STICKER_WIDTH - MARGIN - qr_width, desc_qr_y - desc_qr_height)
            
            # Description text
            p.setFont("Helvetica", small_font)
            p.drawString(MARGIN + 0.2*cm, desc_qr_y - 0.8*cm, product_name[:50])  # Limit to 50 chars
            
            # QR Code 1
            qr = qrcode.make(rec.name)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                qr.save(tmp.name)
                p.drawImage(tmp.name, STICKER_WIDTH - MARGIN - qr_width + 0.2*cm, 
                            desc_qr_y - desc_qr_height + 0.2*cm, 
                            width=qr_width - 0.4*cm, height=qr_width - 0.4*cm)

            # Product title
            title_y = desc_qr_y - desc_qr_height - MARGIN
            p.setFont("Helvetica-Bold", large_font)
            p.drawCentredString(STICKER_WIDTH/2, title_y - 0.8*cm, "OTHER - FOR CONTAINER PHILIPS")

            # Order Info Table (No Border)
            info_table_y = title_y - 1.2*cm
            info_table_height = 4*cm
            
            # Left side - Order info
            p.setFont("Helvetica-Bold", medium_font)
            p.drawString(MARGIN + 0.2*cm, info_table_y - 0.8*cm, "Order Date")
            p.drawString(MARGIN + (STICKER_WIDTH - 2*MARGIN)/2 + 0.2*cm, info_table_y - 0.8*cm, "Due Date")
            
            p.setFont("Helvetica", large_font)
            p.drawString(MARGIN + 0.2*cm, info_table_y - 1.6*cm, create_date_str)
            p.drawString(MARGIN + (STICKER_WIDTH - 2*MARGIN)/2 + 0.2*cm, info_table_y - 1.6*cm, due_date_str)
            
            # QR Code label
            p.setFont("Helvetica-Bold", large_font)
            p.drawCentredString(STICKER_WIDTH/2, info_table_y - 2.8*cm, "QR")
            
            # Underlined text
            p.setFont("Helvetica-Bold", xlarge_font)
            p.drawString(MARGIN + 0.2*cm, info_table_y - 3.8*cm, "MAPH")
            p.line(MARGIN + 0.2*cm, info_table_y - 4.0*cm, MARGIN + 2.5*cm, info_table_y - 4.0*cm)
            
            # Country codes
            p.setFont("Helvetica", large_font)
            p.drawString(MARGIN + 0.2*cm, info_table_y - 4.8*cm, "FRE")
            p.drawString(MARGIN + (STICKER_WIDTH - 2*MARGIN)/2 + 0.2*cm, info_table_y - 4.8*cm, "USA")
            
            # Right side - Image
            if logo_img:
                p.drawImage(logo_img, STICKER_WIDTH - MARGIN - 2.5*cm, info_table_y - 4.0*cm, 
                            width=2.0*cm, height=2.0*cm, preserveAspectRatio=True)

            # Description & Right Box Table
            desc_box_y = info_table_y - info_table_height - MARGIN
            desc_box_height = 1.5*cm
            p.rect(MARGIN, desc_box_y - desc_box_height, STICKER_WIDTH - 2*MARGIN, desc_box_height, stroke=1, fill=0)
            
            # Right box divider
            box_width = 1.5*cm
            p.line(STICKER_WIDTH - MARGIN - box_width, desc_box_y, 
                STICKER_WIDTH - MARGIN - box_width, desc_box_y - desc_box_height)
            
            # Description text
            p.setFont("Helvetica", small_font)
            p.drawString(MARGIN + 0.2*cm, desc_box_y - 0.8*cm, product_name[:60])  # Limit to 60 chars
            
            # Right box content
            p.setFont("Helvetica-Bold", medium_font)
            p.drawCentredString(STICKER_WIDTH - MARGIN - box_width/2, desc_box_y - 0.5*cm, "FPS")
            p.line(STICKER_WIDTH - MARGIN - box_width + 0.2*cm, desc_box_y - 1.0*cm, 
                STICKER_WIDTH - MARGIN - 0.2*cm, desc_box_y - 1.0*cm)
            p.drawCentredString(STICKER_WIDTH - MARGIN - box_width/2, desc_box_y - 1.8*cm, "QC")

            # QR2 Table (No Border)
            qr2_y = desc_box_y - desc_box_height - MARGIN
            qr2_height = 1.5*cm
            
            # QR Code 2
            qr2 = qrcode.make(f"{rec.name}_2")
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                qr2.save(tmp.name)
                p.drawImage(tmp.name, MARGIN + 0.2*cm, qr2_y - qr2_height + 0.2*cm, 
                            width=1.0*cm, height=1.0*cm)
                p.drawImage(tmp.name, STICKER_WIDTH - MARGIN - 1.2*cm, qr2_y - qr2_height + 0.2*cm, 
                            width=1.0*cm, height=1.0*cm)
            
            # QR2 labels
            p.setFont("Helvetica-Bold", medium_font)
            p.drawString(MARGIN + 1.5*cm, qr2_y - 0.5*cm, "No item")
            p.drawString(MARGIN + 1.5*cm, qr2_y - 1.0*cm, "Name")
            p.drawString(MARGIN + 1.5*cm, qr2_y - 1.5*cm, "Due Date")

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
            'url': f'/web/content/{attachment.id}?download=false',
            'target': 'new',
        }