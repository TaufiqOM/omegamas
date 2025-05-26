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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import KeepTogether
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

    def export_to_laporan_pdf(self, export_date=None):
        """
        Method untuk mengekspor data payslip ke dalam file PDF dengan:
        - Penataan kolom yang lebih terstruktur seperti Excel
        - Grup kolom yang logis (Pendapatan, Potongan, dll)
        - Warna header yang membedakan grup
        """
        if not export_date:
            export_date = fields.Date.context_today(self)

        buffer = io.BytesIO()

        # Buat dokumen PDF ukuran landscape A3 dengan margin kecil
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A3),
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )

        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles dengan font kecil tapi readable
        wrap_style = ParagraphStyle(
            name='Wrapped',
            parent=styles['Normal'],
            alignment=TA_LEFT,
            fontSize=5,
            leading=5,
            spaceAfter=1
        )
        
        header_style = ParagraphStyle(
            name='Header',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=5,
            textColor=colors.black,
            spaceAfter=1,
            fontName='Helvetica-Bold',
            leading=5
        )
        
        # Warna untuk grup kolom berbeda
        group_colors = {
            'info': colors.HexColor('#D9E1F2'),  # Biru muda untuk info karyawan
            'pendapatan': colors.HexColor('#E2EFDA'),  # Hijau muda untuk pendapatan
            'tunjangan': colors.HexColor('#FFF2CC'),  # Kuning muda untuk tunjangan
            'potongan': colors.HexColor('#FCE4D6'),  # Oranye muda untuk potongan
            'pajak': colors.HexColor('#F4B084'),  # Oranye lebih tua untuk pajak
            'total': colors.HexColor('#BDD7EE'),  # Biru untuk total
        }

        # Format tanggal
        bulan_dict = {
            '01': 'Januari', '02': 'Februari', '03': 'Maret', '04': 'April',
            '05': 'Mei', '06': 'Juni', '07': 'Juli', '08': 'Agustus',
            '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Desember'
        }

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

        # Header laporan
        batch_name = self[0].payslip_run_id.name if self[0].payslip_run_id else "Gaji Karyawan"
        
        elements.append(Paragraph(f"<b>LAPORAN PERHITUNGAN GAJI - {batch_name}</b>", 
                                ParagraphStyle(name='Title', fontSize=7, alignment=TA_CENTER)))
        elements.append(Paragraph(f"<b>Tanggal Cetak:</b> {formatted_date}", 
                                ParagraphStyle(name='Subtitle', fontSize=5, alignment=TA_CENTER)))
        elements.append(Spacer(1, 0.5*cm))

        # ===================== STRUCTURED TABLE LAYOUT =====================
        
        # Data untuk tabel
        data = []
        
        # 1. HEADER UTAMA (GROUP HEADERS)
        header_row1 = []
        
        # Grup Informasi Karyawan (11 kolom)
        header_row1.append(Paragraph("INFORMASI KARYAWAN", 
                                ParagraphStyle(name='GroupHeader', fontSize=5, 
                                                alignment=TA_CENTER, 
                                                backColor=group_colors['info'])))
        header_row1.extend([''] * 10)  # Placeholder untuk colspan
        
        # Grup Pendapatan (1 kolom)
        header_row1.append(Paragraph("GAJI POKOK", 
                                ParagraphStyle(name='GroupHeader', fontSize=5, 
                                                alignment=TA_CENTER, 
                                                backColor=group_colors['pendapatan'])))
        
        # Grup Tunjangan (10 kolom)
        header_row1.append(Paragraph("TUNJANGAN", 
                                ParagraphStyle(name='GroupHeader', fontSize=5, 
                                                alignment=TA_CENTER, 
                                                backColor=group_colors['tunjangan'])))
        header_row1.extend([''] * 9)  # Placeholder untuk colspan
        
        # Grup Subtotal Pendapatan (2 kolom) - DIUBAH DARI 3 MENJADI 2 KOLOM
        header_row1.append(Paragraph("SUBTOTAL PENDAPATAN", 
                                ParagraphStyle(name='GroupHeader', fontSize=5, 
                                                alignment=TA_CENTER, 
                                                backColor=group_colors['pendapatan'])))
        header_row1.append('')  # Placeholder untuk colspan
        
        # Grup Potongan (15 kolom)
        header_row1.append(Paragraph("POTONGAN", 
                                ParagraphStyle(name='GroupHeader', fontSize=5, 
                                                alignment=TA_CENTER, 
                                                backColor=group_colors['potongan'])))
        header_row1.extend([''] * 14)  # Placeholder untuk colspan
        
        # Grup Pajak (1 kolom)
        header_row1.append(Paragraph("PAJAK", 
                                ParagraphStyle(name='GroupHeader', fontSize=5, 
                                                alignment=TA_CENTER, 
                                                backColor=group_colors['pajak'])))
        
        # Grup Total (2 kolom)
        header_row1.append(Paragraph("TOTAL", 
                                ParagraphStyle(name='GroupHeader', fontSize=5, 
                                                alignment=TA_CENTER, 
                                                backColor=group_colors['total'])))
        header_row1.append('')  # Placeholder untuk colspan
        
        data.append(header_row1)
        
        # 2. SUB-HEADER (KOLOM DETAIL)
        header_row2 = []
        
        # Informasi Karyawan
        info_headers = [
            "No", "Nama", "NO Karyawan", "Posisi", "Dept", 
            "Gol", "Status", "Tgl Masuk", "Tgl Keluar", "Lama Kerja", "PTKP"
        ]
        for h in info_headers:
            header_row2.append(Paragraph(h, header_style))
        
        # Gaji Pokok
        header_row2.append(Paragraph("Basic", header_style))
        
        # Tunjangan
        tunjangan_headers = [
            "JKM", "JKK", "JHT Comp", "BPJS Kesehatan", "JP Comp",
            "T. Tidak Tetap", "Lain-lain", "Jabatan", "Insentif", "Makan"
        ]
        for h in tunjangan_headers:
            header_row2.append(Paragraph(h, header_style))
        
        # Subtotal Pendapatan (2 kolom) - DIUBAH DARI 3 MENJADI 2 KOLOM
        pendapatan_headers = [
            "Sub Gross", "Tunj. Pajak"  # "Gross" dihapus
        ]
        for h in pendapatan_headers:
            header_row2.append(Paragraph(h, header_style))
        
        # Potongan
        potongan_headers = [
            "BPJS JKK", "BPJS JKM", "JHT Emp", "JHT Comp", "BPJS K Comp",
            "BPJS Kes Emp", "JP Comp", "JP Emp", "Meal", "Terlambat",
            "Pulang Dini", "Meninggalkan Pekerjaan", "Pinjaman", "(P) Tunj. Tidak Tetap", "(P) Gaji"
        ]
        for h in potongan_headers:
            header_row2.append(Paragraph(h, header_style))
        
        # Pajak
        header_row2.append(Paragraph("PPH21", header_style))
        
        # Total
        total_headers = [
            "Total Potongan", "Gaji Bersih"
        ]
        for h in total_headers:
            header_row2.append(Paragraph(h, header_style))
        
        data.append(header_row2)
        
        # 3. DATA PAYSLIP
        nomor = 1
        for payslip in self:
            # Data karyawan
            barcode = payslip.employee_id.barcode or "-"
            department_name = payslip.employee_id.department_id.name.split(" / ")[-1] if payslip.employee_id.department_id.name else "-"
            job_name = payslip.employee_id.job_id.name or "-"
            tipe_karyawan = (payslip.employee_type or "-").title()
            contract_type = payslip.contract_id.contract_type_id.name if payslip.contract_id else "-"
            tanggal_bergabung = payslip.contract_id.date_start.strftime('%d-%m-%Y') if payslip.contract_id.date_start else "-"
            tanggal_berhenti = "-"
            status_pajak = dict(payslip.employee_id._fields['l10n_id_kode_ptkp'].selection).get(payslip.employee_id.l10n_id_kode_ptkp, "-")
            
            # Lama kerja
            if payslip.contract_id.date_start:
                start_date = payslip.contract_id.date_start
                today_date = date.today()
                delta = relativedelta.relativedelta(today_date, start_date)
                lama_kerja = f"{delta.years}th {delta.months}bln" if delta.years else f"{delta.months}bln"
            else:
                lama_kerja = "-"
            
            # Baris data
            row_data = [
                Paragraph(str(nomor), wrap_style),
                Paragraph(payslip.employee_id.name, wrap_style),
                Paragraph(barcode, wrap_style),
                Paragraph(job_name, wrap_style),
                Paragraph(department_name, wrap_style),
                Paragraph(tipe_karyawan, wrap_style),
                Paragraph(contract_type, wrap_style),
                Paragraph(tanggal_bergabung, wrap_style),
                Paragraph(tanggal_berhenti, wrap_style),
                Paragraph(lama_kerja, wrap_style),
                Paragraph(status_pajak, wrap_style)
            ]
            
            # Data numerik dengan format yang konsisten
            numeric_fields = [
                'basic_wage',  # Gaji pokok
                
                # Tunjangan
                't_jkm', 't_jkk', 't_jht_comp', 't_bpjs_kesehatan', 't_jp_company',
                't_tidak_tetap', 't_lain_lain', 't_jabatan', 't_insentif', 't_makan',
                
                # Subtotal pendapatan - DIUBAH DARI 3 MENJADI 2 FIELD
                'sub_gross', 't_pph21',  # 'gross_wage' dihapus
                
                # Potongan
                'p_bpjs_jkk', 'p_bpjs_jkm', 'p_jht_employee', 'p_jht_comp', 'p_bpjs_kes_comp',
                'p_bpjs_kes_emp', 'p_jp_company', 'p_jp_employee', 'p_meal', 'p_terlambat',
                'p_pd', 'p_mp', 'p_pinjaman', 'p_tunj_tidak_tetap', 'p_gaji',
                
                # Pajak
                'p_pph21',
                
                # Total
                'p_potongan', 'net_wage'
            ]
            
            for field_name in numeric_fields:
                field_value = getattr(payslip, field_name, 0.0)
                formatted_value = f"{field_value:,.0f}" if field_value == int(field_value) else f"{field_value:,.2f}"
                row_data.append(Paragraph(formatted_value, wrap_style))
            
            data.append(row_data)
            nomor += 1
        
        # 4. BARIS TOTAL
        total_row = [Paragraph("TOTAL", 
                            ParagraphStyle(name='TotalHeader', fontSize=4.5, 
                                        alignment=TA_CENTER, 
                                        backColor=group_colors['total']))]
        total_row.extend([''] * (len(info_headers)-1))
        
        # Hitung total untuk setiap field numerik
        for field_name in numeric_fields:
            total = sum(getattr(payslip, field_name, 0.0) for payslip in self)
            total_row.append(Paragraph(f"{total:,.0f}" if total == int(total) else f"{total:,.2f}", 
                                    ParagraphStyle(name='TotalText', fontSize=4.5, 
                                                alignment=TA_RIGHT, 
                                                textColor=colors.black,
                                                fontName='Helvetica-Bold')))
        
        data.append(total_row)
        
        # ===================== TABLE FORMATTING =====================
        
        # Lebar kolom yang lebih proporsional
        col_widths = [
            0.4*cm,  # No
            0.95*cm,  # Nama
            1.5*cm,  # ID
            0.95*cm,  # Posisi
            0.95*cm,  # Dept
            0.95*cm,  # Gol
            0.95*cm,  # Status
            0.95*cm,  # Tgl Masuk
            0.95*cm,  # Tgl Keluar
            0.95*cm,  # Lama
            0.95*cm,  # Pajak
            
            # Gaji Pokok
            1.1*cm,
            
            # Tunjangan (10 kolom)
            *[0.95*cm for _ in range(10)],
            
            # Subtotal Pendapatan (2 kolom) - DIUBAH DARI 3 MENJADI 2 KOLOM
            *[1.1*cm for _ in range(2)],
            
            # Potongan (15 kolom)
            *[0.95*cm for _ in range(15)],
            
            # Pajak
            0.95*cm,
            
            # Total (2 kolom)
            *[1.1*cm for _ in range(2)],
        ]
        
        # Buat tabel
        table = Table(data, colWidths=col_widths, repeatRows=2, hAlign='LEFT')
        
        # Style untuk tabel
        table_style = TableStyle([
            # Span untuk group headers
            ('SPAN', (0, -1), (10, -1)),
            ('SPAN', (0, 0), (10, 0)),  # Informasi Karyawan
            ('SPAN', (11, 0), (11, 0)),  # Gaji Pokok
            ('SPAN', (12, 0), (21, 0)),  # Tunjangan
            ('SPAN', (22, 0), (23, 0)),  # Subtotal Pendapatan (DIUBAH DARI (22,0)-(24,0))
            ('SPAN', (24, 0), (38, 0)),  # Potongan (DIUBAH KARENA GROSS DIHAPUS)
            ('SPAN', (39, 0), (39, 0)),  # Pajak (DIUBAH KARENA GROSS DIHAPUS)
            ('SPAN', (40, 0), (41, 0)),  # Total (DIUBAH KARENA GROSS DIHAPUS)
            
            # Background group headers
            ('BACKGROUND', (0, 0), (10, 0), group_colors['info']),
            ('BACKGROUND', (11, 0), (11, 0), group_colors['pendapatan']),
            ('BACKGROUND', (12, 0), (21, 0), group_colors['tunjangan']),
            ('BACKGROUND', (22, 0), (23, 0), group_colors['pendapatan']),  # DIUBAH DARI (22,0)-(24,0)
            ('BACKGROUND', (24, 0), (38, 0), group_colors['potongan']),  # DIUBAH KARENA GROSS DIHAPUS
            ('BACKGROUND', (39, 0), (39, 0), group_colors['pajak']),  # DIUBAH KARENA GROSS DIHAPUS
            ('BACKGROUND', (40, 0), (41, 0), group_colors['total']),  # DIUBAH KARENA GROSS DIHAPUS
            
            # Background sub-headers
            ('BACKGROUND', (0, 1), (10, 1), colors.lightgrey),
            ('BACKGROUND', (11, 1), (11, 1), colors.lightgrey),
            ('BACKGROUND', (12, 1), (21, 1), group_colors['tunjangan']),
            ('BACKGROUND', (22, 1), (23, 1), group_colors['pendapatan']),  # DIUBAH DARI (22,1)-(24,1)
            ('BACKGROUND', (24, 1), (38, 1), group_colors['potongan']),  # DIUBAH KARENA GROSS DIHAPUS
            ('BACKGROUND', (39, 1), (39, 1), group_colors['pajak']),  # DIUBAH KARENA GROSS DIHAPUS
            ('BACKGROUND', (40, 1), (41, 1), group_colors['total']),  # DIUBAH KARENA GROSS DIHAPUS
            
            # Border
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            
            # Alignment
            ('ALIGN', (11, 2), (-1, -1), 'RIGHT'),  # Angka rata kanan
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Font
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('LEADING', (0, 0), (-1, -1), 7),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            
            # Total row style
            ('BACKGROUND', (0, -1), (41, -1), group_colors['total']),  # DIUBAH DARI (0,-1)-(42,-1)
            ('FONTNAME', (0, -1), (41, -1), 'Helvetica-Bold'),  # DIUBAH DARI (0,-1)-(42,-1)
            ('TEXTCOLOR', (0, -1), (41, -1), colors.black),  # DIUBAH DARI (0,-1)-(42,-1)
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        
        # ===================== SIGNATURE BELOW TABLE =====================
        # Buat frame untuk signature yang akan dipindahkan ke halaman berikutnya jika tidak cukup space
        signature_frame = KeepTogether([
            Spacer(1, 1*cm),  # space before signature
            
            Paragraph("Direktur", ParagraphStyle(
                name='SignatureTitle', 
                fontSize=7,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )),
            Spacer(1, 1.5*cm),  # space for signature line
            
            Paragraph("Alex Graham Bell", ParagraphStyle(
                name='SignatureName', 
                fontSize=7,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )),
            
            # Tambahkan spacer ekstra untuk memastikan ada cukup ruang
            Spacer(1, 2*cm)
        ])

        elements.append(signature_frame)

        # Build PDF
        doc.build(elements)
        pdf_value = buffer.getvalue()
        buffer.close()

        # Buat attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'Payslip_Laporan_{batch_name}_{formatted_date.split()[0]}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_value),
            'res_model': 'hr.payslip',
            'res_id': self[0].id if self else False,
            'mimetype': 'application/pdf'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=false',
            'target': 'new',
        }

