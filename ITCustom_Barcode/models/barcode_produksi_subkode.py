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

            # Columns widths for first table
            col1_width = total_inner_width * 0.25
            col2_width = total_inner_width * 0.50
            col3_width = total_inner_width * 0.25

            # First table (header)
            header_height = 1.5 * cm  # Adjusted height for image
            header_table_y = STICKER_HEIGHT - MARGIN

            # Draw logo in column 1 first table (scaled within cell size)
            if logo_img:
                logo_width, logo_height = logo_img.getSize()
                max_cell_width = col1_width
                max_cell_height = header_height
                desired_height = max_cell_height  # Use full height without padding
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

            p.setStrokeColor(colors.black)
            p.setLineWidth(1)

            # Draw first table outer rectangle
            p.rect(MARGIN, header_table_y - header_height, total_inner_width, header_height, stroke=1, fill=0)

            # Vertical lines for first table columns
            p.line(MARGIN + col1_width, header_table_y, MARGIN + col1_width, header_table_y - header_height)
            p.line(MARGIN + col1_width + col2_width, header_table_y, MARGIN + col1_width + col2_width, header_table_y - header_height)

            # Draw "4444" centered in column 2 of first table
            p.setFont("Helvetica-Bold", medium_font + 6)
            # Adjust vertical position for better centering by subtracting 2 points
            default_code = rec.produk_id.default_code if rec.produk_id else "NoCode"
            p.drawCentredString(MARGIN + col1_width + col2_width / 2, header_table_y - header_height / 2 - 2, default_code)

            # Draw formatted date centered in column 3 of first table
            p.setFont("Helvetica-Bold", medium_font + 6)
            # Add space between month and year in month_year_str
            if rec.create_date:
                dt = rec.create_date
                if isinstance(dt, str):
                    dt = datetime.datetime.strptime(dt, "%Y-%m-%d").date()
                month_year_str = dt.strftime('%b')[0:3] + " " + dt.strftime('%y')
            else:
                month_year_str = "NoDate"
            p.drawCentredString(MARGIN + col1_width + col2_width + col3_width / 2, header_table_y - header_height / 2 - 2, month_year_str)

            # Second table below with gap, no outermost border removed
            second_table_height = 2.5 * cm  # Doubled the height (2x the header height)
            gap_between_tables = 0.2 * cm
            second_table_y = header_table_y - header_height - gap_between_tables

            # Draw second table outer rectangle (border)
            p.rect(MARGIN, second_table_y - second_table_height, total_inner_width, second_table_height, stroke=1, fill=0)

            # Second table columns widths
            second_col1_width = total_inner_width * 0.75
            second_col2_width = total_inner_width * 0.25

            # Vertical line separating second table columns
            p.line(MARGIN + second_col1_width, second_table_y, MARGIN + second_col1_width, second_table_y - second_table_height)

            # Draw text in first column left aligned from top
            p.setFont("Helvetica", medium_font)
            text_x = MARGIN + 0.2 * cm
            text_y = second_table_y - medium_font * 1.2  # Position from top like QR Order text
            client_order_ref = rec.order_id.client_order_ref if rec.order_id else "No Client Order Ref"
            p.drawString(text_x, text_y, client_order_ref)

            # Calculate available height in second table
            available_height = second_table_height - (2 * medium_font)  # Reserve space for text above and below

            # Add "QR Order" text above QR code
            p.setFont("Helvetica-Bold", medium_font)
            qr_text = "QR Order"
            qr_text_width = p.stringWidth(qr_text, "Helvetica-Bold", medium_font)
            qr_text_x = MARGIN + second_col1_width + (second_col2_width - qr_text_width) / 2
            qr_text_y = second_table_y - medium_font * 1.2  # Position from top of table

            p.drawString(qr_text_x, qr_text_y, qr_text)

            # Generate QR code for second column from client_order_ref
            qr = qrcode.make(client_order_ref or "NoCode", border=0)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                qr.save(tmp.name)
                qr_size = min(available_height * 0.7, second_col2_width * 0.7)  # Size constrained by height and width
                qr_x = MARGIN + second_col1_width + (second_col2_width - qr_size) / 2
                qr_y = second_table_y - medium_font * 2 - qr_size  # Position below "QR Order" text
                p.drawImage(tmp.name, qr_x, qr_y, width=qr_size, height=qr_size)

            # Add partner_id text below QR code from client_order_ref
            p.setFont("Helvetica", medium_font - 1)
            partner_name = client_order_ref
            partner_text_width = p.stringWidth(partner_name, "Helvetica", medium_font - 1)
            partner_text_x = MARGIN + second_col1_width + (second_col2_width - partner_text_width) / 2
            partner_text_y = qr_y - medium_font * 1.2  # Position below QR code

            p.drawString(partner_text_x, partner_text_y, partner_name)

            # Add third row without border
            third_row_gap = 0.4 * cm  # Increased margin top for spacing
            third_row_y = second_table_y - second_table_height - third_row_gap
            p.setFont("Helvetica-Bold", medium_font)
            third_row_text = f"OTHER - FOR CONTAINER {partner_name}"
            p.drawString(MARGIN, third_row_y, third_row_text)

            # Tambahkan baris keempat dengan dua kolom utama
            fourth_row_gap = 0.8 * cm  # Increased top margin between row 3 and row 4
            fourth_row_y = third_row_y - medium_font - fourth_row_gap
            fourth_row_height = (medium_font - 1) * 3 * 2  # Adjusted height to fit larger MAPH text without overflow

            # Draw outer rectangle for fourth row table with top margin
            top_margin = 0.2 * cm

            # Hitung lebar kolom utama (masing-masing 50%)
            main_col_width = (STICKER_WIDTH - 2 * MARGIN) / 2
            
            # Baris pertama kolom kiri dibagi menjadi dua sub-kolom
            sub_col_width = main_col_width / 2

            # Removed outer rectangle for fourth row table
            # p.rect(MARGIN, fourth_row_y - fourth_row_height - top_margin, STICKER_WIDTH - 2 * MARGIN, fourth_row_height, stroke=1, fill=0)

            # Draw vertical lines for main columns in fourth row
            # Removed vertical line for main columns in fourth row
            # p.line(MARGIN + main_col_width, fourth_row_y, MARGIN + main_col_width, fourth_row_y - fourth_row_height - top_margin)

            # Draw vertical line for sub-columns in left main column
            # Removed vertical line for sub-columns in left main column
            # p.line(MARGIN + sub_col_width, fourth_row_y, MARGIN + sub_col_width, fourth_row_y - fourth_row_height - top_margin)

            # Additional removal: Remove stroke color and line width settings that might affect borders
            p.setStrokeColorRGB(1, 1, 1)  # Set stroke color to white to hide any remaining borders
            p.setLineWidth(0)

            # Restore stroke color and line width before drawing fifth row
            p.setStrokeColorRGB(0, 0, 0)  # Set stroke color back to black
            p.setLineWidth(1)

            # Draw horizontal lines for full border in fourth row
            # Top horizontal line (already drawn by rectangle)
            # Draw horizontal line below "Order Date" and "Due Date" labels
            line1_y = fourth_row_y - medium_font
            # Removed this line to remove border between date and due date
            # p.line(MARGIN, line1_y, MARGIN + STICKER_WIDTH - 2 * MARGIN, line1_y)

            # Draw horizontal line below dates and partner name (approximate)
            line2_y = fourth_row_y - medium_font * 3.5
            # Removed this line to remove border below partner_name
            # p.line(MARGIN, line2_y, MARGIN + STICKER_WIDTH - 2 * MARGIN, line2_y)

            # Draw horizontal line below MAPH text (approximate)
            line3_y = line2_y - (medium_font - 1) * 3 * 2
            # Removed this line to remove border below partner_name
            # p.line(MARGIN, line3_y, MARGIN + STICKER_WIDTH - 2 * MARGIN, line3_y)
            
            # Bagian Tanggal Order
            p.setFont("Helvetica", medium_font)
            p.drawString(MARGIN + 0.2 * cm, fourth_row_y - medium_font, "Order Date")
            
            p.setFont("Helvetica-Bold", medium_font + 1)
            order_date = rec.order_id.blanket_order_id.date_create_blanket_order if rec.order_id and rec.order_id.blanket_order_id else "-"
            if isinstance(order_date, str):
                formatted_order_date = order_date
            else:
                formatted_order_date = order_date.strftime('%d %b %y') if order_date else "-"  # Format: DD Month YY
            # Draw date without border or line
            p.drawString(MARGIN + 0.2 * cm, fourth_row_y - medium_font * 2.2, formatted_order_date)

            # Bagian Tanggal Jatuh Tempo
            p.setFont("Helvetica", medium_font)
            p.drawString(MARGIN + sub_col_width + 0.2 * cm, fourth_row_y - medium_font, "Due Date")
            
            p.setFont("Helvetica-Bold", medium_font + 1)
            due_date = rec.order_id.due_date_order if rec.order_id else "-"
            if isinstance(due_date, str):
                formatted_due_date = due_date
            else:
                formatted_due_date = due_date.strftime('%d %b %y') if due_date else "-"  # Format: DD Month YY
            # Draw date without border or line
            p.drawString(MARGIN + sub_col_width + 0.2 * cm, fourth_row_y - medium_font * 2.2, formatted_due_date)

            # Draw partner name first
            partner_row_y = fourth_row_y - medium_font * 4  # Reduced top margin for partner_name above MAPH

            # Add MAPH text below partner name (bold dan underline)
            maph_y = partner_row_y - medium_font * 3  # Increased top margin for MAPH text below partner name

            # Add FRE and USA text in two columns below MAPH
            fre_usa_y = maph_y - medium_font * 3  # Increased top margin for FRE and USA text
            p.setFont("Helvetica", medium_font + 1)
            # Replace partner_name with client_order_ref for partner_name below due date and order date
            partner_name_below = rec.order_id.client_order_ref if rec.order_id else "No Client Order Ref"
            p.drawString(MARGIN + 0.2 * cm, partner_row_y, partner_name_below)
            
            # Add MAPH text below partner name (bold dan underline)
            maph_y = partner_row_y - medium_font * 3  # Increased top margin for MAPH text below partner name
            p.setFont("Helvetica-Bold", (medium_font - 1) * 3)
            # Replace MAPH text with company_registry from partner
            maph_text = rec.order_id.partner_id.company_registry if rec.order_id and rec.order_id.partner_id else "No Company Registry"
            maph_x = MARGIN + 0.2 * cm
            p.drawString(maph_x, maph_y, maph_text)
            
            # Draw underline for MAPH text
            text_width = p.stringWidth(maph_text, "Helvetica-Bold", (medium_font - 1) * 3)
            p.line(maph_x, maph_y - 1, maph_x + text_width, maph_y - 1)
            
            # Add FRE and USA text in two columns below MAPH
            fre_usa_y = maph_y - medium_font * 1.5  # Position below MAPH
            p.setFont("Helvetica", medium_font + 1)
            
            # Calculate column widths and positions
            col_width = main_col_width / 2
            
            # Draw FRE in first column
            p.drawString(MARGIN + 0.2 * cm, fre_usa_y, "FRE")
            
            # Draw USA in second column right aligned
            usa_text = "USA"
            usa_x = MARGIN + col_width * 2 - p.stringWidth(usa_text, "Helvetica", medium_font + 1) - 0.2 * cm
            p.drawString(usa_x, fre_usa_y, usa_text)
            
            # Add fifth row with 85% and 15% width columns
            fifth_row_y = fre_usa_y - medium_font * 1.5  # Position below FRE/USA row
            
            # Create fifth row table with two columns (85% and 15%) - increased height for sections
            border_height = medium_font * 2 + 1.5 * cm  # Height for top section + 1.5cm middle + bottom section
            table_y = fifth_row_y - border_height + medium_font * 0.3
            
            # Draw outer rectangle for table
            p.rect(MARGIN, table_y, total_inner_width, border_height, stroke=1, fill=0)
            
            # Calculate column widths (90% and 10%)
            left_col_width = total_inner_width * 0.90
            right_col_width = total_inner_width * 0.10
            
            
            # Draw vertical line separating columns
            vertical_line_x = MARGIN + left_col_width
            p.line(vertical_line_x, table_y, vertical_line_x, table_y + border_height)
            
            # Draw text in columns from top of table
            p.setFont("Helvetica", medium_font - 1)
            text_y = table_y + border_height - medium_font * 1.2  # Position from top like second table
            
            # Draw lorem15 text in left column (85% width)
            p.drawString(MARGIN + 0.2 * cm, text_y, "lorem15")
            
            # Draw horizontal lines to separate sections in right column
            top_section_height = medium_font * 2  # Height for FPS section
            bottom_section_height = medium_font * 2  # Height for QC section
            
            # Draw horizontal line below FPS section
            first_line_y = table_y + border_height - top_section_height
            p.line(MARGIN + left_col_width, first_line_y, MARGIN + total_inner_width, first_line_y)
            
            # Draw horizontal line above QC section
            second_line_y = table_y + bottom_section_height
            p.line(MARGIN + left_col_width, second_line_y, MARGIN + total_inner_width, second_line_y)
            
            # Draw texts in right column (15% width) - center aligned
            right_col_width = total_inner_width - left_col_width
            
            # Top section - FPS (centered)
            fps_text = "FPS"
            fps_width = p.stringWidth(fps_text, "Helvetica", medium_font - 1)
            fps_x = MARGIN + left_col_width + (right_col_width - fps_width) / 2
            top_y = table_y + border_height - (top_section_height / 2) - medium_font / 2
            p.drawString(fps_x, top_y, fps_text)
            
            # Middle section is empty (1.5cm space)
            
            # Bottom section - QC (centered)
            qc_text = "QC"
            qc_width = p.stringWidth(qc_text, "Helvetica", medium_font - 1)
            qc_x = MARGIN + left_col_width + (right_col_width - qc_width) / 2
            bottom_y = table_y + (bottom_section_height / 2) - medium_font / 2
            p.drawString(qc_x, bottom_y, qc_text)

            # Add sixth row with three columns (20%, 60%, 20%)
            sixth_row_gap = 0.4 * cm
            sixth_row_y = table_y - sixth_row_gap
            row_height = 2.5 * cm  # Height for QR codes and text
            
            # Calculate column widths
            col1_width = total_inner_width * 0.20
            col2_width = total_inner_width * 0.60
            col3_width = total_inner_width * 0.20
            
            # Generate and draw QR codes
            qr_size = min(col1_width * 0.9, row_height * 0.9)  # QR code size constrained by column width and height
            
            # Left column - QR Item text (not bold) and QR code
            p.setFont("Helvetica", medium_font - 1)
            qr_text = "QR Item"
            text_width = p.stringWidth(qr_text, "Helvetica", medium_font - 1)
            text_x = MARGIN + (col1_width - text_width) / 2
            text_y = sixth_row_y - medium_font * 1.2
            p.drawString(text_x, text_y, qr_text)
            
            # Left QR code (centered)
            qr = qrcode.make(rec.name or "NoCode", border=2)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                qr.save(tmp.name)
                qr_x = MARGIN + (col1_width - qr_size) / 2
                qr_y = sixth_row_y - row_height + (row_height - qr_size) / 2 - medium_font
                p.drawImage(tmp.name, qr_x, qr_y, width=qr_size, height=qr_size)
            
            # Center column - vertically centered content
            center_content_height = (medium_font * 4)  # Total height of all text elements
            start_y = sixth_row_y - (row_height - center_content_height) / 2  # Start position for centered content
            
            # No Item text (adjusted spacing)
            p.setFont("Helvetica-Bold", medium_font - 1)
            header_text = "No Item"
            header_width = p.stringWidth(header_text, "Helvetica-Bold", medium_font - 1)
            header_x = MARGIN + col1_width + (col2_width - header_width) / 2
            header_y = start_y - medium_font * 0.3  # Increased spacing from name
            p.drawString(header_x, header_y, header_text)
            
            # Name text (larger and bold, centered)
            name_font_size = medium_font + 5  # Increased font size
            p.setFont("Helvetica-Bold", name_font_size)
            name_text = rec.name or "NoCode"
            name_width = p.stringWidth(name_text, "Helvetica-Bold", name_font_size)
            name_x = MARGIN + col1_width + (col2_width - name_width) / 2
            name_y = sixth_row_y - row_height / 2  # Adjusted vertical position
            p.drawString(name_x, name_y, name_text)
            
            # Center column - create date
            if rec.create_date:
                dt = rec.create_date
                if isinstance(dt, str):
                    dt = datetime.datetime.strptime(dt, "%Y-%m-%d").date()
                formatted_date = dt.strftime('%d %b %Y')
            else:
                formatted_date = "-"
            
            date_font_size = medium_font - 1  # Same size as "No Item"
            date_width = p.stringWidth(formatted_date, "Helvetica", date_font_size)
            date_x = MARGIN + col1_width + (col2_width - date_width) / 2
            date_y = name_y - date_font_size * 1.5
            p.setFont("Helvetica", date_font_size)
            p.drawString(date_x, date_y, formatted_date)
            
            # Right column - QR Item text (not bold) and QR code
            p.setFont("Helvetica", medium_font - 1)  # Not bold
            text_x = MARGIN + col1_width + col2_width + (col3_width - text_width) / 2
            p.drawString(text_x, text_y, qr_text)
            
            # Right QR code
            qr = qrcode.make(rec.name or "NoCode", border=2)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                qr.save(tmp.name)
                qr_x = MARGIN + col1_width + col2_width + (col3_width - qr_size) / 2
                qr_y = sixth_row_y - row_height + (row_height - qr_size) / 2 - medium_font
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
