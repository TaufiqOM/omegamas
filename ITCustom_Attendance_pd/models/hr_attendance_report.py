from odoo import models, fields, api
import datetime

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    pulang_dini_true = fields.Integer(string='Pulang Dini True', compute='_compute_pulang_dini_true', store=True)
    pd_hitung = fields.Integer(string='Menit Pulang Dini', compute='_compute_pulang_dini_true', store=True)

    @api.depends('check_in', 'check_out')
    def _compute_pulang_dini_true(self):
        for record in self:
            record.pulang_dini_true = 0  # Default value
            record.pd_hitung = 0  # Default value
            if record.check_in and record.check_out:
                # Konversi check_in dan check_out ke waktu lokal (WIB - UTC+7)
                check_in_local = record.check_in + datetime.timedelta(hours=7)
                check_out_local = record.check_out + datetime.timedelta(hours=7)
                check_in_date = check_in_local.date()

                # Dapatkan semua record absensi untuk tanggal yang sama
                attendance_records = [
                    rec for rec in record.employee_id.attendance_ids
                    if rec.check_in and (rec.check_in + datetime.timedelta(hours=7)).date() == check_in_date
                ]

                # Ambil work_to dari schedule
                work_to = 0
                calendar = record.employee_id.contract_id.resource_calendar_id
                if calendar:
                    for attendance in calendar.attendance_ids:
                        if attendance.dayofweek == str(check_in_date.weekday()) and attendance.day_period == 'afternoon':
                            work_to = attendance.hour_to
                            break

                # Konversi work_to ke waktu datetime dengan aman
                hours = int(work_to)
                minutes = int(round((work_to - hours) * 60))
                work_to_time = datetime.time(hours, minutes)
                work_to_datetime = datetime.datetime.combine(check_in_date, work_to_time)

                # Cek apakah hari tersebut adalah hari kerja (Senin - Jumat)
                is_weekday = check_in_date.weekday() < 5

                # Cek apakah tanggal tersebut adalah hari libur berdasarkan Working Schedule
                is_holiday = False
                if calendar and calendar.global_leave_ids:
                    for leave in calendar.global_leave_ids:
                        if leave.date_from.date() <= check_in_date <= leave.date_to.date():
                            is_holiday = True
                            break

                # Hitung hanya untuk check-out terakhir di hari tersebut dan jika hari kerja & bukan libur
                max_record_id = max([rec.id for rec in attendance_records]) if attendance_records else None
                if record.id == max_record_id:
                    if is_weekday and not is_holiday:
                        if check_out_local < work_to_datetime:
                            record.pulang_dini_true = 1
                            delta = work_to_datetime - check_out_local
                            record.pd_hitung = int(delta.total_seconds() // 60)
                        else:
                            record.pulang_dini_true = 0
                            record.pd_hitung = 0
                    else:
                        record.pulang_dini_true = 0
                        record.pd_hitung = 0
