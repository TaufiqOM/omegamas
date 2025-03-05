from odoo import models, fields, api
from datetime import datetime, timedelta, timezone

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    terlambat = fields.Integer(string='Terlambat (Detik)', compute='_compute_terlambat', store=True)

    @api.depends('check_in', 'x_studio_work_from')
    def _compute_terlambat(self):
        wib_offset = timedelta(hours=7)
        for record in self:
            if record.check_in and record.x_studio_work_from:
                # Konversi x_studio_work_from (float) ke waktu (HH:MM:SS)
                work_from_hour = int(record.x_studio_work_from)
                work_from_minute = int((record.x_studio_work_from - work_from_hour) * 60)
                work_from_time = timedelta(hours=work_from_hour, minutes=work_from_minute)

                # Ambil waktu dari check_in dan konversi ke timedelta dalam UTC+7
                check_in_dt = fields.Datetime.from_string(record.check_in).replace(tzinfo=timezone.utc) + wib_offset
                check_in_time = timedelta(hours=check_in_dt.hour, minutes=check_in_dt.minute, seconds=check_in_dt.second)

                # Hitung selisih waktu dalam detik
                terlambat = (check_in_time - work_from_time).total_seconds()

                # Jika terlambat negatif (check_in lebih awal), set ke 0
                record.terlambat = max(int(terlambat), 0)
            else:
                record.terlambat = 0
