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
        import base64
        from io import BytesIO
        from reportlab.lib import colors
        import datetime

        STICKER_WIDTH = 10 * cm
        STICKER_HEIGHT = 15 * cm
        MARGIN = 0.2 * cm

        pdf_buffer = BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=(STICKER_WIDTH, STICKER_HEIGHT))

        medium_font = 9

        company = self.env.company
        logo_img = None
        if company.logo:
            logo_stream = BytesIO(base64.b64decode(company.logo))
            logo_img = ImageReader(logo_stream)

        for rec in self:
            if rec.create_date:
                dt = rec.create_date
                if isinstance(dt, str):
                    dt = datetime.datetime.strptime(dt, "%Y-%m-%d").date()
                month_year_str = dt.strftime('%b')[0:3] + dt.strftime('%y')
            else:
                month_year_str = "NoDate"

            total_inner_width = STICKER_WIDTH - 2 * MARGIN

            # First table (header)
            header_height = 1.3 * cm
            header_table_y = STICKER_HEIGHT - MARGIN

            p.setStrokeColor(colors.black)
            p.setLineWidth(1)

            # Draw first table outer rectangle
            p.rect(MARGIN, header_table_y - header_height, total_inner_width, header_height, stroke=1, fill=0)

            # Columns widths for first table
            col1_width = total_inner_width * 0.25
            col2_width = total_inner_width * 0.50
            col3_width = total_inner_width * 0.25

            # Vertical lines for first table columns
            p.line(MARGIN + col1_width, header_table_y, MARGIN + col1_width, header_table_y - header_height)
            p.line(MARGIN + col1_width + col2_width, header_table_y, MARGIN + col1_width + col2_width, header_table_y - header_height)

            # Draw logo in column 1 first table (scaled within cell size)
            if logo_img:
                logo_width, logo_height = logo_img.getSize()
                max_cell_width = col1_width
                max_cell_height = header_height
                desired_height = max_cell_height * 0.9
                scale = desired_height / logo_height
                desired_width = logo_width * scale
                if desired_width > max_cell_width * 0.9:
                    scale = (max_cell_width * 0.9) / logo_width
                    desired_width = logo_width * scale
                    desired_height = logo_height * scale
                x_pos = MARGIN + (max_cell_width - desired_width) / 2
                y_pos = header_table_y - max_cell_height + (max_cell_height - desired_height) / 2
                p.drawImage(logo_img, x_pos, y_pos, width=desired_width, height=desired_height, preserveAspectRatio=True, mask='auto')
            else:
                p.setFont("Helvetica-Bold", medium_font)
                p.drawString(MARGIN + 0.2 * cm, header_table_y - 0.5 * cm, "OM")

            # Draw "4444" centered in column 2 of first table
            p.setFont("Helvetica-Bold", medium_font)
            p.drawCentredString(MARGIN + col1_width + col2_width / 2, header_table_y - header_height / 2, "4444")

            # Draw formatted date right aligned in column 3 of first table
            p.drawRightString(MARGIN + col1_width + col2_width + col3_width - 0.2 * cm, header_table_y - header_height / 2, month_year_str)

            # Second table below with gap, no outermost border removed
            second_table_height = 1.0 * cm
            gap_between_tables = 0.2 * cm
            second_table_y = header_table_y - header_height - gap_between_tables

            # Draw second table outer rectangle (border)
            p.rect(MARGIN, second_table_y - second_table_height, total_inner_width, second_table_height, stroke=1, fill=0)

            # Second table columns widths
            second_col1_width = total_inner_width * 0.75
            second_col2_width = total_inner_width * 0.25

            # Vertical line separating second table columns
            p.line(MARGIN + second_col1_width, second_table_y, MARGIN + second_col1_width, second_table_y - second_table_height)

            # Draw dummy text "lorem 10" in first column left aligned
            p.setFont("Helvetica", medium_font)
            text_x = MARGIN + 0.2 * cm
            text_y = second_table_y - second_table_height / 2 - medium_font / 4  # approx vertical align center
            p.drawString(text_x, text_y, "lorem 10")

            # Generate QR code for second column
            qr = qrcode.make(rec.name or "NoCode")
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                qr.save(tmp.name)
                qr_size = second_table_height * 0.9
                qr_x = MARGIN + second_col1_width + (second_col2_width - qr_size) / 2
                qr_y = second_table_y - second_table_height + (second_table_height - qr_size) / 2
                p.drawImage(tmp.name, qr_x, qr_y, width=qr_size, height=qr_size)

            p.showPage()

        p.save()
        pdf_buffer.seek(0)

        pdf_file = base64.b64encode(pdf_buffer.read())
        pdf_buffer.close()

        attachment = self.env['ir.attachment'].create({
            'name': 'Barcode_QRCode_tables_with_qrcode.pdf',
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
