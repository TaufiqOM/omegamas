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

        # Format tanggal wizard
        if export_date:
            bulan = export_date.strftime('%m')
            bulan_text = bulan_dict.get(bulan, 'Tidak Valid')
            formatted_date = export_date.strftime(f'%d {bulan_text} %Y')
        else:
            formatted_date = datetime.today().strftime('%d %B %Y')

        # Ambil batch name dari payslip
        batch_name = self[0].payslip_run_id.name if self[0].payslip_run_id else "Gaji Karyawan"

        # **Baris dimulai dari baris 8**
        row = 7  # Baris dimulai dari 8 (indeks 7)

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

        # Ambil semua komponen gaji yang ada di struktur gaji payslip
        salary_structure = self[0].struct_id
        salary_rule_ids = salary_structure.rule_ids.filtered(lambda r: r.appears_on_payslip)

        # Kelompokkan komponen gaji berdasarkan kategori
        allowance_rules = salary_rule_ids.filtered(lambda r: r.category_id.code in ['ALW', 'COMP'])  # Allowance
        deduction_rules = salary_rule_ids.filtered(lambda r: r.category_id.code == 'DED')  # Deduction
        other_rules = salary_rule_ids - allowance_rules - deduction_rules  # Komponen sisa

        # **Tulis header dengan merge dua baris hanya sampai kolom 12**
        col = 0
        for header in headers[:12]:  # Hanya sampai kolom 12 (indeks 11)
            worksheet.merge_range(row, col, row + 1, col, header, header_style)  # Merge dua baris
            col += 1

        # **Tulis header komponen sisa dengan merge atas dan bawah**
        for rule in other_rules:
            worksheet.merge_range(row, col, row + 1, col, rule.name, header_style)  # Merge dua baris
            col += 1

        # **Tulis header "Tunjangan" di atas komponen gaji dengan kategori Allowance**
        if allowance_rules:
            # Tentukan kolom awal dan akhir untuk merge header "Tunjangan"
            start_col = col
            end_col = col + len(allowance_rules) - 1

            # Merge header "Tunjangan" ke kanan sampai akhir kategori yang relevan
            worksheet.merge_range(row, start_col, row, end_col, "Tunjangan", tunjangan_header_style)

            # Tulis header komponen gaji di bawah header "Tunjangan"
            for rule in allowance_rules:
                worksheet.write(row + 1, col, rule.name, header_style)
                col += 1

        # **Tulis header "Potongan" di atas komponen gaji dengan kategori Deduction**
        if deduction_rules:
            # Tentukan kolom awal dan akhir untuk merge header "Potongan"
            start_col = col
            end_col = col + len(deduction_rules) - 1

            # Merge header "Potongan" ke kanan sampai akhir kategori yang relevan
            worksheet.merge_range(row, start_col, row, end_col, "Potongan", potongan_header_style)

            # Tulis header komponen gaji di bawah header "Potongan"
            for rule in deduction_rules:
                worksheet.write(row + 1, col, rule.name, header_style)
                col += 1

        row += 2  # Pindah ke baris setelah header yang digabung

        nomor = 1  # Mulai dari 1

        # **Mengisi Data Payslip**
        for payslip in self:
            barcode = payslip.employee_id.barcode or "Tidak Ada"
            department_name = payslip.employee_id.department_id.name.split(" / ")[-1] if payslip.employee_id.department_id.name else "Tidak Ada"
            job_name = payslip.employee_id.job_id.name or "Tidak Ada"
            tipe_karyawan = payslip.employee_id.x_studio_tipe_karyawan or "Tidak Ada"
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

            # Isi data untuk setiap komponen gaji yang ada di struktur gaji payslip
            col = 11  # Mulai dari kolom 11
            for rule in other_rules:
                line = payslip.line_ids.filtered(lambda l: l.salary_rule_id.id == rule.id)
                amount = line.total if line else 0.0
                worksheet.write(row, col, amount, normal)
                col += 1

            for rule in allowance_rules:
                line = payslip.line_ids.filtered(lambda l: l.salary_rule_id.id == rule.id)
                amount = line.total if line else 0.0
                worksheet.write(row, col, amount, normal)
                col += 1

            for rule in deduction_rules:
                line = payslip.line_ids.filtered(lambda l: l.salary_rule_id.id == rule.id)
                amount = line.total if line else 0.0
                worksheet.write(row, col, amount, normal)
                col += 1

            row += 1
            nomor += 1  # Tambah nomor urut

        # Auto-fit lebar kolom berdasarkan isi data
        for col_num in range(len(headers) + len(other_rules) + len(allowance_rules) + len(deduction_rules)):
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