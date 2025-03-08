from odoo import models, fields, api
import datetime

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    presensi = fields.Integer(compute='_compute_absen', store=True)

    @api.depends('check_in', 'check_out')
    def _compute_absen(self):
        for record in self:
            if record.check_in and record.check_out:
                # Konversi check_in ke waktu lokal (WIB - UTC+7)
                check_in_utc = record.check_in
                check_in_local = check_in_utc + datetime.timedelta(hours=7)
                check_in_date = check_in_local.date()

                employee_id = record.employee_id.id

                # Dapatkan semua record absensi untuk tanggal yang sama
                attendance_records = []
                if record.employee_id and record.employee_id.attendance_ids:
                    for rec in record.employee_id.attendance_ids:
                        if rec.check_in:
                            rec_check_in_utc = rec.check_in
                            rec_check_in_local = rec_check_in_utc + datetime.timedelta(hours=7)
                            if rec_check_in_local.date() == check_in_date:
                                attendance_records.append(rec)

                # Cari check-in pertama pada hari itu
                first_check_in = None
                if attendance_records:
                    first_check_in = min(attendance_records, key=lambda r: r.check_in)

                # Cek apakah hari tersebut adalah hari kerja (Senin - Jumat)
                is_weekday = check_in_date.weekday() < 5

                # Cek apakah tanggal tersebut adalah hari libur berdasarkan Working Schedule
                is_holiday = False
                if record.employee_id and record.employee_id.contract_id and record.employee_id.contract_id.resource_calendar_id:
                    for leave in record.employee_id.contract_id.resource_calendar_id.global_leave_ids:
                        leave_date_from = leave.date_from.date()
                        leave_date_to = leave.date_to.date()
                        if leave_date_from <= check_in_date <= leave_date_to:
                            is_holiday = True
                            break

                # Jika ini adalah check-in pertama pada hari kerja dan bukan hari libur → 1, jika tidak → 0
                if first_check_in and record.id == first_check_in.id:
                    record.presensi = 1 if is_weekday and not is_holiday else 0
                else:
                    record.presensi = 0
            else:
                record.presensi = 0

    @api.model
    def compute_old_data(self):
        records = self.search([])
        records._compute_absen()
