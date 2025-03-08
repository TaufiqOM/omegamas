from odoo import models, fields, api
from datetime import timedelta

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    hari = fields.Char(string="Hari (WIB)", compute="_compute_hari", store=True)
    check_in_count = fields.Integer(string="Check-in Order", compute="_compute_check_in_count", store=True)

    @api.depends('check_in')
    def _compute_hari(self):
        days = {
            0: 'Senin', 1: 'Selasa', 2: 'Rabu',
            3: 'Kamis', 4: 'Jum’at', 5: 'Sabtu', 6: 'Minggu'
        }
        for record in self:
            if record.check_in:
                check_in = record.check_in

                # Konversi Manual UTC ke WIB (Tambahkan 7 jam)
                jam_baru = check_in.hour + 7
                hari_baru = check_in.weekday()

                # Jika melebihi 24 jam, geser ke hari berikutnya
                if jam_baru >= 24:
                    jam_baru -= 24  # Sesuaikan kembali dalam 0-23 jam
                    hari_baru += 1  # Geser ke hari berikutnya

                    # Jika hari_baru melebihi 6 (Minggu), kembali ke 0 (Senin)
                    if hari_baru > 6:
                        hari_baru = 0

                # Set hasil hari dalam WIB
                record.hari = days[hari_baru]
            else:
                record.hari = ''
    
    @api.depends('check_in', 'employee_id')
    def _compute_check_in_count(self):
        for record in self:
            if record.check_in and record.employee_id:
                check_in_date = record.check_in.date()
                # Cari semua check-in pada hari yang sama untuk karyawan yang sama
                check_ins = self.env['hr.attendance'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('check_in', '>=', check_in_date),
                    ('check_in', '<', check_in_date + timedelta(days=1))
                ], order='check_in asc')
                
                # Urutkan berdasarkan waktu check_in (jika belum terurut)
                sorted_check_ins = check_ins.sorted(key=lambda r: r.check_in)
                
                # Tentukan urutan check-in
                for index, check_in_record in enumerate(sorted_check_ins, start=1):
                    if check_in_record.id == record.id:
                        record.check_in_count = index
                        break
            else:
                record.check_in_count = 0