from odoo import models, fields, api
import base64
import io
import xlsxwriter
from datetime import date, datetime
from dateutil import relativedelta

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
        Format A3 Landscape dengan wrap text untuk kolom yang panjang.
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

        # Set page orientation to landscape and paper size to A3
        worksheet.set_landscape()
        worksheet.set_paper(8)  # 8 is the code for A3 paper size

        # Style
        info_style = workbook.add_format({
            'align': 'left', 
            'text_wrap': True,
            'num_format': '#,##0'
        })
        
        normal = workbook.add_format({
            'align': 'left', 
            'text_wrap': True,
            'border': 1,
            'num_format': '#,##0'
        })
        header_style = workbook.add_format({
            'align': 'center', 
            'valign': 'vcenter', 
            'bold': True, 
            'border': 1,
            'text_wrap': True
        })
        tunjangan_header_style = workbook.add_format({
            'align': 'center', 
            'valign': 'vcenter', 
            'bold': True, 
            'bg_color': '#D3D3D3', 
            'border': 1,
            'text_wrap': True
        })
        potongan_header_style = workbook.add_format({
            'align': 'center', 
            'valign': 'vcenter', 
            'bold': True, 
            'bg_color': '#FFCCCB', 
            'border': 1,
            'text_wrap': True
        })
        total_style = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
            'border': 1,
            'num_format': '#,##0'
        })

        # Dictionary nama bulan dalam Bahasa Indonesia
        bulan_dict = {
            '01': 'Januari', '02': 'Februari', '03': 'Maret', '04': 'April',
            '05': 'Mei', '06': 'Juni', '07': 'Juli', '08': 'Agustus',
            '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Desember'
        }

        # Format tanggal wizard
        if export_date:
            bulan = export_date.strftime('%m')
            bulan_text = bulan_dict.get(bulan, 'Tidak Valid')
            formatted_date = export_date.strftime(f'%d {bulan_text} %Y')
        else:
            formatted_date = datetime.today().strftime('%d %B %Y')

        # Ambil batch name dari payslip
        batch_name = self[0].payslip_run_id.name if self[0].payslip_run_id else "Gaji Karyawan"

        # **Baris dimulai dari baris 2 (indeks 1)**
        row = 2  # Baris dimulai dari 2 (indeks 1)

        # **Header Laporan** - tanpa border
        worksheet.write(row, 0, "Periode Penggajian", info_style)
        worksheet.write(row, 1, f": {batch_name}", info_style)

        row += 1
        worksheet.write(row, 0, "Referensi Mata Uang", info_style)
        worksheet.write(row, 1, ": Pajak", info_style)

        row += 1
        worksheet.write(row, 0, "Tanggal", info_style)
        worksheet.write(row, 1, f": {formatted_date}", info_style)

        row += 2  # Spasi sebelum tabel data

        # **Header tabel** - dihapus "Tanggal Berhenti"
        headers = [
            "Nomor", "Nama Karyawan", "No. Karyawan", "Posisi", "Departemen", 
            "Golongan", "Status Kepegawaian", "Tanggal Bergabung", 
            "Lama Kerja", "Status Pajak"
        ]

        # Daftar field dengan optional="show" dari XML
        optional_show_fields = [
            'basic_wage', 't_jkm', 't_jkk', 't_jht_comp', 't_bpjs_kesehatan', 't_jp_company', 
            't_tidak_tetap', 't_lain_lain', 't_jabatan', 't_insentif', 't_makan', 'sub_gross', 't_pph21', 'p_bpjs_jkk', 'p_bpjs_jkm', 'p_jht_employee', 'p_jht_comp', 'p_bpjs_kes_comp', 'p_bpjs_kes_emp', 
            'p_jp_company', 'p_jp_employee', 'p_meal', 'p_terlambat', 'p_pd', 'p_mp',
            'p_pinjaman', 'p_gaji', 'p_potongan', 'p_pph21', 'net_wage'
        ]

        # **Tulis header dengan merge dua baris**
        col = 0
        for header in headers:  # Sekarang hanya 10 kolom header
            worksheet.merge_range(row, col, row + 1, col, header, header_style)  # Merge dua baris
            col += 1

        # **Tulis header khusus untuk kolom setelah header utama**
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

        # Total Pendapatan (merge ke bawah)
        worksheet.merge_range(row, col, row + 1, col, "Total Pendapatan", header_style)
        col += 1

        # Tunjangan Pajak (merge ke bawah)
        worksheet.merge_range(row, col, row + 1, col, "Tunjangan Pajak", header_style)
        col += 1

        # Potongan (header dengan colspan)
        worksheet.merge_range(row, col, row, col + 13, "Potongan", potongan_header_style)
        # Sub-header untuk Potongan
        potongan_sub_headers = [
            '(P) BPJS JKK', '(P) BPJS JKM', '(P) JHT Employee', '(P) JHT Comp', '(P) BPJS Kesehatan Company', 
            '(P) BPJS Kes Emp', '(P) JP Company', '(P) JP Employee', '(P) Meal', '(P) Terlambat', 
            '(P) Pulang Dini', '(P) Meninggalkan Pekerjaan', '(P) Pinjaman', '(P) Potongan Gaji'
        ]
        for i, sub_header in enumerate(potongan_sub_headers):
            worksheet.write(row + 1, col + i, sub_header, potongan_header_style)
        col += len(potongan_sub_headers)

        # Total Potongan (merge ke bawah)
        worksheet.merge_range(row, col, row + 1, col, "Total Potongan", header_style)
        col += 1

        # Pajak (merge ke bawah)
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
            
            # Hitung lama kerja
            if payslip.contract_id.date_start:
                start_date = payslip.contract_id.date_start
                today_date = date.today()
                delta = relativedelta.relativedelta(today_date, start_date)
                lama_kerja = f"{delta.years} tahun {delta.months} bulan" if delta.years else f"{delta.months} bulan"
            else:
                lama_kerja = "Tidak Ada"

            worksheet.write(row, 8, lama_kerja, normal)  # Kolom lama kerja sekarang di index 8
            worksheet.write(row, 9, status_pajak, normal)  # Kolom status pajak sekarang di index 9

            # Isi data untuk setiap field yang memiliki optional="show"
            col = 10  # Mulai dari kolom setelah header utama (sekarang 10 kolom)
            for field_name in optional_show_fields:
                field_value = getattr(payslip, field_name, 0.0)
                # Format angka dengan pemisah ribuan
                worksheet.write(row, col, field_value, normal)
                col += 1

            row += 1
            nomor += 1  # Tambah nomor urut

        # **Tambahkan baris Total**
        worksheet.merge_range(row, 0, row, 9, "Total", total_style)  # Merge kolom 1-10 (indeks 0-9)

        # **Hitung total untuk setiap kolom yang relevan**
        col = 10  # Mulai dari kolom setelah header utama (sekarang 10 kolom)
        for field_name in optional_show_fields:
            total = sum(getattr(payslip, field_name, 0.0) for payslip in self)
            worksheet.write(row, col, total, total_style)
            col += 1

        row += 1  # Pindah ke baris berikutnya setelah baris Total

        # Set zoom to 80% to fit more content
        worksheet.set_zoom(80)

        # Auto-fit lebar kolom berdasarkan isi data dengan wrap text
        for col_num in range(len(headers) + len(optional_show_fields)):
            # Set column width with wrap text
            if col_num < len(headers):
                # For header columns, set width based on header length
                header_width = len(headers[col_num]) + 5  # Add some padding
                worksheet.set_column(col_num, col_num, min(header_width, 30))  # Max width 30
            else:
                # For data columns, set a fixed width that works for most cases
                worksheet.set_column(col_num, col_num, 15)  # Fixed width for data columns

        # Set margins to fit A3 landscape
        worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
        
        # Set print area to include all columns
        worksheet.print_area(0, 0, row, len(headers) + len(optional_show_fields) - 1)

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
    