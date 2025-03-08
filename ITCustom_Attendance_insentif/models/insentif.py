from odoo import models, fields, api
from datetime import timedelta, timezone
import logging

_logger = logging.getLogger(__name__)

class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    insentif = fields.Integer(string="Insentif", compute="_compute_insentif", store=True, help="1 jika karyawan mendapatkan insentif, 0 jika tidak.")
    status_insentif = fields.Selection([
        ('setuju', 'Setuju'),
        ('tolak', 'Tolak')
    ], string="Status Insentif", default='', compute="_compute_status_insentif", inverse="_inverse_status_insentif", store=True)
    catatan = fields.Text(string="Catatan")

    @api.depends('check_in', 'check_out')
    def _compute_insentif(self):
        for record in self:
            if record.check_in and record.check_out:
                # Gunakan zona waktu Indonesia WIB (UTC+7)
                wib_offset = 7
                check_in_local = record.check_in + timedelta(hours=wib_offset)
                check_in_date = check_in_local.date()
                
                # Hitung selisih waktu dalam jam
                time_diff = (record.check_out - record.check_in).total_seconds() / 3600
                
                # Dapatkan semua record absensi untuk tanggal yang sama
                attendance_records = [rec for rec in record.employee_id.attendance_ids if rec.check_in and (rec.check_in + timedelta(hours=wib_offset)).date() == check_in_date]
                
                # Cari check-in pertama pada hari itu
                first_check_in = min(attendance_records, key=lambda r: r.check_in) if attendance_records else None
                
                # Cek apakah hari tersebut adalah hari libur (Sabtu atau Minggu)
                is_weekend = check_in_date.weekday() in [5, 6]  # 5 = Sabtu, 6 = Minggu
                
                # Cek apakah tanggal tersebut adalah hari libur berdasarkan Working Schedule
                is_holiday = any(
                    leave.date_from.date() <= check_in_date <= leave.date_to.date()
                    for leave in record.employee_id.contract_id.resource_calendar_id.global_leave_ids
                ) if record.employee_id.contract_id and record.employee_id.contract_id.resource_calendar_id else False
                
                # Debugging log
                _logger.info("ID: %s, Time Diff: %s, First Check-in: %s, Weekend: %s, Holiday: %s",
                    record.id, time_diff, first_check_in.id if first_check_in else None, is_weekend, is_holiday)
                
                # Jika ini adalah check-in pertama pada hari libur atau akhir pekan dan minimal 4 jam kerja → 1, jika tidak → 0
                if time_diff >= 4 and first_check_in and record.id == first_check_in.id and (is_weekend or is_holiday):
                    record.insentif = 1
                else:
                    record.insentif = 0
            else:
                record.insentif = 0

    @api.depends('insentif')
    def _compute_status_insentif(self):
        for record in self:
            if record.insentif == 1:
                record.status_insentif = 'setuju'
            else:
                record.status_insentif = ''

    def _inverse_status_insentif(self):
        for record in self:
            if record.status_insentif != 'setuju':
                record.insentif = 0
            elif record.status_insentif == 'setuju':
                record.insentif = 1
