# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_Payroll_button_mandiri_bca/models/custom_payroll_laporan.py
from odoo import models, fields, api
import base64
import io
import xlsxwriter
from datetime import date, datetime
from dateutil import relativedelta
from zoneinfo import ZoneInfo
from io import BytesIO
from reportlab.lib.pagesizes import landscape, A3
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
import base64

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    export_date = fields.Date(string="Tanggal Pembayaran", default=fields.Date.context_today)

    def open_export_laporan_modal(self):
        """
        Membuka wizard custom untuk memilih tanggal pembayaran.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pilih Tanggal Pembayaran',
            'res_model': 'hr.payslip.wizard.laporan',
            'view_mode': 'form',
            'target': 'new',
        }

    def export_to_laporan(self, export_date=None):
        """
        Method untuk mengekspor data payslip ke dalam file Excel.
        Baris dimulai dari baris 8, dan header memiliki dua baris yang digabung hanya sampai kolom 12.
        Tambahkan header "Tunjangan" di atas komponen gaji dengan kategori Allowance.
        Tambahkan header "Potongan" di atas komponen gaji dengan kategori Deduction.
        """
        if not self:
            return

        # Ambil export_date dari context jika tidak disediakan sebagai parameter
        if not export_date:
            export_date = self.env.context.get('export_date', fields.Date.context_today(self))

        # Buat file Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Laporan Payslip")

        # Style
        normal = workbook.add_format({'align': 'left'})
        header_style = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 1})
        tunjangan_header_style = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
        potongan_header_style = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'bg_color': '#FFCCCB', 'border': 1})  # Warna berbeda untuk Potongan

        # Dictionary nama bulan dalam Bahasa Indonesia
        bulan_dict = {
            '01': 'Januari', '02': 'Februari', '03': 'Maret', '04': 'April',
            '05': 'Mei', '06': 'Juni', '07': 'Juli', '08': 'Agustus',
            '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Desember'
        }

        # Format tanggal dengan jam dan menit otomatis dalam WIB
        if export_date:
            bulan = export_date.strftime('%m')
            bulan_text = bulan_dict.get(bulan, 'Tidak Valid')
            
            # Dapatkan waktu sekarang dalam WIB
            jakarta_tz = ZoneInfo('Asia/Jakarta')  # Untuk Python 3.9+
            # jakarta_tz = pytz.timezone('Asia/Jakarta')  # Untuk Python < 3.9
            current_time = datetime.now(jakarta_tz).strftime('%H:%M')
            
            formatted_date = export_date.strftime(f'%d {bulan_text} %Y') + f' {current_time} WIB'
        else:
            jakarta_tz = ZoneInfo('Asia/Jakarta')
            # jakarta_tz = pytz.timezone('Asia/Jakarta')
            current_time = datetime.now(jakarta_tz).strftime('%H:%M')
            formatted_date = datetime.today().strftime('%d %B %Y') + f' {current_time} WIB'

        # Ambil batch name dari payslip
        batch_name = self[0].payslip_run_id.name if self[0].payslip_run_id else "Gaji Karyawan"

        # **Baris dimulai dari baris 8**
        row = 2  # Baris dimulai dari 8 (indeks 7)

        # **Header Laporan**
        worksheet.write(row, 0, "Periode Penggajian", normal)
        worksheet.write(row, 1, f": {batch_name}", normal)

        row += 1
        worksheet.write(row, 0, "Referensi Mata Uang", normal)
        worksheet.write(row, 1, ": Pajak", normal)

        row += 1
        worksheet.write(row, 0, "Tanggal", normal)
        worksheet.write(row, 1, f": {formatted_date}", normal)

        row += 2  # Spasi sebelum tabel data

        # **Header tabel**
        headers = [
            "Nomor", "Nama Karyawan", "No. Karyawan", "Posisi", "Departemen", 
            "Golongan", "Status Kepegawaian", "Tanggal Bergabung", 
            "Tanggal Berhenti", "Lama Kerja", "Status Pajak"
        ]

        # Daftar field dengan optional="show" dari XML
        optional_show_fields = [
            'basic_wage', 't_jkm', 't_jkk', 't_jht_comp', 't_bpjs_kesehatan', 't_jp_company', 
            't_tidak_tetap', 't_lain_lain', 't_jabatan', 't_insentif', 't_makan', 'sub_gross', 't_pph21', 
            'gross_wage', 'p_bpjs_jkk', 'p_bpjs_jkm', 'p_jht_employee', 'p_jht_comp', 'p_bpjs_kes_comp', 'p_bpjs_kes_emp', 
            'p_jp_company', 'p_jp_employee', 'p_meal', 'p_terlambat', 'p_pd', 'p_mp',
            'p_pinjaman', 'p_tunj_tidak_tetap', 'p_gaji', 'p_potongan', 'p_pph21', 'net_wage'
        ]

        # **Tulis header dengan merge dua baris hanya sampai kolom 10**
        col = 0
        for header in headers[:11]:  # Hanya sampai kolom 10 (indeks 10)
            worksheet.merge_range(row, col, row + 1, col, header, header_style)  # Merge dua baris
            col += 1

        # **Tulis header khusus untuk kolom 11 ke atas**
        # Basic Wage (merge ke bawah)
        worksheet.merge_range(row, col, row + 1, col, "Basic Wage", header_style)
        col += 1

        # Tunjangan (header dengan colspan)
        worksheet.merge_range(row, col, row, col + 9, "Tunjangan", tunjangan_header_style)
        # Sub-header untuk Tunjangan
        tunjangan_sub_headers = [
            '(T) JKM', '(T) JKK', '(T) JHT Comp', '(T) BPJS Kesehatan', '(T) JP Company',
            '(T) Tidak Tetap', '(T) Lain Lain', '(T) Jabatan', '(T) Insentif', '(T) Makan'
        ]
        for i, sub_header in enumerate(tunjangan_sub_headers):
            worksheet.write(row + 1, col + i, sub_header, tunjangan_header_style)
        col += len(tunjangan_sub_headers)

        # Gross Wage (merge ke bawah)
        worksheet.merge_range(row, col, row + 1, col, "Total Pendapatan", header_style)
        col += 1

        # Gross Wage (merge ke bawah)
        worksheet.merge_range(row, col, row + 1, col, "Tunjangan Pajak", header_style)
        col += 1

        # Gross Wage (merge ke bawah)
        worksheet.merge_range(row, col, row + 1, col, "Gaji Kotor", header_style)
        col += 1

        # Potongan (header dengan colspan)
        worksheet.merge_range(row, col, row, col + 14, "Potongan", potongan_header_style)
        # Sub-header untuk Potongan
        potongan_sub_headers = [
            '(P) BPJS JKK', '(P) BPJS JKM', '(P) JHT Employee', '(P) JHT Comp', '(P) BPJS Kesehatan Company', '(P) BPJS Kes Emp', 
            '(P) JP Company', '(P) JP Employee', '(P) Meal', '(P) Terlambat', '(P) Pulang Dini', '(P) Meninggalkan Pekerjaan',
            '(P) Pinjaman', '(P) Potongan Tidan Tetap', '(P) Potongan Gaji'
        ]
        for i, sub_header in enumerate(potongan_sub_headers):
            worksheet.write(row + 1, col + i, sub_header, potongan_header_style)
        col += len(potongan_sub_headers)

        # Total Potongan (merge ke bawah)
        worksheet.merge_range(row, col, row + 1, col, "Total Potongan", header_style)
        col += 1

        worksheet.merge_range(row, col, row + 1, col, "Pajak", header_style)
        col += 1

        # Net Wage (merge ke bawah)
        worksheet.merge_range(row, col, row + 1, col, "Net Wage", header_style)
        col += 1

        row += 2  # Pindah ke baris setelah header yang digabung

        nomor = 1  # Mulai dari 1

        # **Mengisi Data Payslip**
        for payslip in self:
            barcode = payslip.employee_id.barcode or "Tidak Ada"
            department_name = payslip.employee_id.department_id.name.split(" / ")[-1] if payslip.employee_id.department_id.name else "Tidak Ada"
            job_name = payslip.employee_id.job_id.name or "Tidak Ada"
            tipe_karyawan = (payslip.employee_type or "Tidak Ada").title()
            contract_type = payslip.contract_id.contract_type_id.name if payslip.contract_id else "Tidak Ada"
            tanggal_bergabung = payslip.contract_id.date_start.strftime('%d-%m-%Y') if payslip.contract_id.date_start else ""
            tanggal_berhenti = ""
            status_pajak = dict(payslip.employee_id._fields['l10n_id_kode_ptkp'].selection).get(payslip.employee_id.l10n_id_kode_ptkp, "Tidak Ada")

            # **Tulis data payslip ke dalam Excel**
            worksheet.write(row, 0, nomor, normal)
            worksheet.write(row, 1, payslip.employee_id.name, normal)
            worksheet.write(row, 2, barcode, normal)
            worksheet.write(row, 3, job_name, normal)
            worksheet.write(row, 4, department_name, normal)
            worksheet.write(row, 5, tipe_karyawan, normal)
            worksheet.write(row, 6, contract_type, normal)
            worksheet.write(row, 7, tanggal_bergabung, normal)
            worksheet.write(row, 8, tanggal_berhenti, normal)
            
            # Hitung lama kerja
            if payslip.contract_id.date_start:
                start_date = payslip.contract_id.date_start
                today_date = date.today()
                delta = relativedelta.relativedelta(today_date, start_date)
                lama_kerja = f"{delta.years} tahun {delta.months} bulan" if delta.years else f"{delta.months} bulan"
            else:
                lama_kerja = "Tidak Ada"

            worksheet.write(row, 9, lama_kerja, normal)  # Kolom 10: Lama Kerja
            worksheet.write(row, 10, status_pajak, normal)  # Kolom 11: Status Pajak

            # Isi data untuk setiap field yang memiliki optional="show"
            col = 11  # Mulai dari kolom 11
            for field_name in optional_show_fields:
                field_value = getattr(payslip, field_name, 0.0)
                worksheet.write(row, col, field_value, normal)
                col += 1

            row += 1
            nomor += 1  # Tambah nomor urut

        # **Tambahkan baris Total**
        worksheet.merge_range(row, 0, row, 10, "Total", header_style)  # Merge kolom 1-11 (indeks 0-10)

        # **Hitung total untuk setiap kolom yang relevan**
        col = 11  # Mulai dari kolom 11 (indeks 11)
        for field_name in optional_show_fields:
            total = sum(getattr(payslip, field_name, 0.0) for payslip in self)
            worksheet.write(row, col, total, header_style)
            col += 1

        row += 1  # Pindah ke baris berikutnya setelah baris Total


        # Auto-fit lebar kolom berdasarkan isi data
        for col_num in range(len(headers) + len(optional_show_fields)):
            worksheet.set_column(col_num, col_num, max(len(str(headers[col_num])) if col_num < len(headers) else 15, 15))  # Minimal lebar 15

        workbook.close()
        output.seek(0)

        # Simpan file sebagai attachment
        file_content = base64.b64encode(output.read())

        attachment = self.env['ir.attachment'].create({
            'name': f'Payslip_Laporan_{formatted_date}.xlsx',
            'type': 'binary',
            'datas': file_content,
            'res_model': 'hr.payslip',
            'res_id': self[0].id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    # Update the export_to_laporan_pdf method in custom_payroll_laporan.py
    def export_to_laporan_pdf(self, export_date=None):
        """
        Method untuk mengekspor data payslip ke dalam file PDF dengan komponen yang sama persis seperti Excel.
        """
        if not export_date:
            export_date = fields.Date.context_today(self)

        buffer = io.BytesIO()

        # Buat dokumen PDF ukuran landscape A3
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A3),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )

        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        wrap_style = ParagraphStyle(
            name='Wrapped',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=8,
            spaceAfter=6
        )
        
        header_style = ParagraphStyle(
            name='Header',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=8,
            textColor=colors.black,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        tunjangan_header_style = ParagraphStyle(
            name='TunjanganHeader',
            parent=header_style,
            backColor=colors.HexColor('#D3D3D3')
        )
        
        potongan_header_style = ParagraphStyle(
            name='PotonganHeader',
            parent=header_style,
            backColor=colors.HexColor('#FFCCCB')
        )

        # Dictionary nama bulan dalam Bahasa Indonesia
        bulan_dict = {
            '01': 'Januari', '02': 'Februari', '03': 'Maret', '04': 'April',
            '05': 'Mei', '06': 'Juni', '07': 'Juli', '08': 'Agustus',
            '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Desember'
        }

        # Format tanggal dengan jam dan menit otomatis dalam WIB
        if export_date:
            bulan = export_date.strftime('%m')
            bulan_text = bulan_dict.get(bulan, 'Tidak Valid')
            jakarta_tz = ZoneInfo('Asia/Jakarta')
            current_time = datetime.now(jakarta_tz).strftime('%H:%M')
            formatted_date = export_date.strftime(f'%d {bulan_text} %Y') + f' {current_time} WIB'
        else:
            jakarta_tz = ZoneInfo('Asia/Jakarta')
            current_time = datetime.now(jakarta_tz).strftime('%H:%M')
            formatted_date = datetime.today().strftime('%d %B %Y') + f' {current_time} WIB'

        # Ambil batch name dari payslip
        batch_name = self[0].payslip_run_id.name if self[0].payslip_run_id else "Gaji Karyawan"

        # Tambahkan informasi laporan
        elements.append(Paragraph(f"Periode Penggajian: {batch_name}", wrap_style))
        elements.append(Paragraph("Referensi Mata Uang: Pajak", wrap_style))
        elements.append(Paragraph(f"Tanggal: {formatted_date}", wrap_style))
        elements.append(Paragraph("<br/><br/>", wrap_style))  # Spasi

        # Header tabel
        headers_main = [
            "Nomor", "Nama Karyawan", "No. Karyawan", "Posisi", "Departemen", 
            "Golongan", "Status Kepegawaian", "Tanggal Bergabung", 
            "Tanggal Berhenti", "Lama Kerja", "Status Pajak"
        ]
        
        # Daftar field dengan optional="show" dari XML
        optional_show_fields = [
            'basic_wage', 't_jkm', 't_jkk', 't_jht_comp', 't_bpjs_kesehatan', 't_jp_company', 
            't_tidak_tetap', 't_lain_lain', 't_jabatan', 't_insentif', 't_makan', 'sub_gross', 't_pph21', 
            'gross_wage', 'p_bpjs_jkk', 'p_bpjs_jkm', 'p_jht_employee', 'p_jht_comp', 'p_bpjs_kes_comp', 'p_bpjs_kes_emp', 
            'p_jp_company', 'p_jp_employee', 'p_meal', 'p_terlambat', 'p_pd', 'p_mp',
            'p_pinjaman', 'p_tunj_tidak_tetap', 'p_gaji', 'p_potongan', 'p_pph21', 'net_wage'
        ]
        
        # Buat struktur data untuk tabel
        data = []
        
        # Baris header pertama (merge beberapa kolom)
        header_row1 = []
        
        # Header utama (kolom 1-11)
        for h in headers_main[:11]:
            header_row1.append(Paragraph(h, header_style))
        
        # Basic Wage
        header_row1.append(Paragraph("Basic Wage", header_style))
        
        # Tunjangan (merge 10 kolom)
        header_row1.append(Paragraph("Tunjangan", tunjangan_header_style))
        header_row1.extend([''] * 9)  # Placeholder untuk colspan
        
        # Total Pendapatan, Tunjangan Pajak, Gaji Kotor
        header_row1.append(Paragraph("Total Pendapatan", header_style))
        header_row1.append(Paragraph("Tunjangan Pajak", header_style))
        header_row1.append(Paragraph("Gaji Kotor", header_style))
        
        # Potongan (merge 15 kolom)
        header_row1.append(Paragraph("Potongan", potongan_header_style))
        header_row1.extend([''] * 14)  # Placeholder untuk colspan
        
        # Total Potongan, Pajak, Net Wage
        header_row1.append(Paragraph("Total Potongan", header_style))
        header_row1.append(Paragraph("Pajak", header_style))
        header_row1.append(Paragraph("Net Wage", header_style))
        
        data.append(header_row1)
        
        # Baris header kedua (sub-header)
        header_row2 = []
        
        # Kolom 1-11 kosong (karena sudah di-merge di atas)
        header_row2.extend([''] * 11)
        
        # Basic Wage (tidak ada sub-header)
        header_row2.append('')
        
        # Sub-header Tunjangan
        tunjangan_sub_headers = [
            '(T) JKM', '(T) JKK', '(T) JHT Comp', '(T) BPJS Kesehatan', '(T) JP Company',
            '(T) Tidak Tetap', '(T) Lain Lain', '(T) Jabatan', '(T) Insentif', '(T) Makan'
        ]
        for h in tunjangan_sub_headers:
            header_row2.append(Paragraph(h, tunjangan_header_style))
        
        # Total Pendapatan, Tunjangan Pajak, Gaji Kotor (tidak ada sub-header)
        header_row2.extend([''] * 3)
        
        # Sub-header Potongan
        potongan_sub_headers = [
            '(P) BPJS JKK', '(P) BPJS JKM', '(P) JHT Employee', '(P) JHT Comp', '(P) BPJS Kesehatan Company', 
            '(P) BPJS Kes Emp', '(P) JP Company', '(P) JP Employee', '(P) Meal', '(P) Terlambat', 
            '(P) Pulang Dini', '(P) Meninggalkan Pekerjaan', '(P) Pinjaman', '(P) Potongan Tidan Tetap', '(P) Potongan Gaji'
        ]
        for h in potongan_sub_headers:
            header_row2.append(Paragraph(h, potongan_header_style))
        
        # Total Potongan, Pajak, Net Wage (tidak ada sub-header)
        header_row2.extend([''] * 3)
        
        data.append(header_row2)
        
        # Isi data payslip
        nomor = 1
        for payslip in self:
            barcode = payslip.employee_id.barcode or "Tidak Ada"
            department_name = payslip.employee_id.department_id.name.split(" / ")[-1] if payslip.employee_id.department_id.name else "Tidak Ada"
            job_name = payslip.employee_id.job_id.name or "Tidak Ada"
            tipe_karyawan = (payslip.employee_type or "Tidak Ada").title()
            contract_type = payslip.contract_id.contract_type_id.name if payslip.contract_id else "Tidak Ada"
            tanggal_bergabung = payslip.contract_id.date_start.strftime('%d-%m-%Y') if payslip.contract_id.date_start else ""
            tanggal_berhenti = ""
            status_pajak = dict(payslip.employee_id._fields['l10n_id_kode_ptkp'].selection).get(payslip.employee_id.l10n_id_kode_ptkp, "Tidak Ada")
            
            # Hitung lama kerja
            if payslip.contract_id.date_start:
                start_date = payslip.contract_id.date_start
                today_date = date.today()
                delta = relativedelta.relativedelta(today_date, start_date)
                lama_kerja = f"{delta.years} tahun {delta.months} bulan" if delta.years else f"{delta.months} bulan"
            else:
                lama_kerja = "Tidak Ada"
            
            # Buat baris data
            row_data = [
                str(nomor),
                Paragraph(payslip.employee_id.name, wrap_style),
                barcode,
                job_name,
                department_name,
                tipe_karyawan,
                contract_type,
                tanggal_bergabung,
                tanggal_berhenti,
                lama_kerja,
                status_pajak
            ]
            
            # Tambahkan field optional
            for field_name in optional_show_fields:
                field_value = getattr(payslip, field_name, 0.0)
                row_data.append(f"{field_value:,.2f}" if isinstance(field_value, (int, float)) else str(field_value))
            
            data.append(row_data)
            nomor += 1
        
        # Tambahkan baris total
        total_row = [Paragraph("Total", header_style)]
        total_row.extend([''] * 10)  # Untuk kolom 1-11
        
        # Hitung total untuk setiap field optional
        col_start = 11  # Kolom pertama setelah header utama
        for i in range(len(optional_show_fields)):
            total = sum(getattr(payslip, optional_show_fields[i], 0.0) for payslip in self)
            total_row.append(f"{total:,.2f}")
        
        data.append(total_row)
        
        # Buat tabel
        table = Table(data, repeatRows=2)
        
        # Style untuk tabel
        table_style = TableStyle([
            # Header style
            ('SPAN', (11, 0), (20, 0)),  # Merge untuk Tunjangan
            ('SPAN', (21, 0), (23, 0)),  # Merge untuk Total Pendapatan, Tunjangan Pajak, Gaji Kotor
            ('SPAN', (24, 0), (38, 0)),  # Merge untuk Potongan
            ('SPAN', (39, 0), (41, 0)),  # Merge untuk Total Potongan, Pajak, Net Wage
            
            # Background header
            ('BACKGROUND', (0, 0), (-1, 1), colors.white),
            ('BACKGROUND', (11, 0), (20, 0), colors.HexColor('#D3D3D3')),  # Tunjangan
            ('BACKGROUND', (24, 0), (38, 0), colors.HexColor('#FFCCCB')),  # Potongan
            
            # Sub-header background
            ('BACKGROUND', (11, 1), (20, 1), colors.HexColor('#D3D3D3')),  # Tunjangan
            ('BACKGROUND', (24, 1), (38, 1), colors.HexColor('#FFCCCB')),  # Potongan
            
            # Border
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Alignment
            ('ALIGN', (11, 2), (-1, -1), 'RIGHT'),  # Angka rata kanan
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Font
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        pdf_value = buffer.getvalue()
        buffer.close()

        # Buat attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'Payslip_Laporan_{formatted_date}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_value),
            'res_model': 'hr.payslip',
            'res_id': self[0].id if self else False,
            'mimetype': 'application/pdf'
        })

        # Return URL untuk membuka PDF di tab baru
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=false',  # download=false untuk mencegah download otomatis
            'target': 'new',  # Buka di tab baru
        }