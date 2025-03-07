from odoo import models, fields, api
from datetime import datetime, timedelta, timezone

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    terlambat_detik = fields.Integer(string='Terlambat Masuk (Detik)', compute='_compute_terlambat_detik', store=True)

    @api.depends('check_in', 'x_studio_work_from')
    def _compute_terlambat_detik(self):
        wib_offset = timedelta(hours=7)
        for record in self:
            if record.check_in and record.x_studio_work_from:
                check_in_dt = fields.Datetime.from_string(record.check_in).replace(tzinfo=timezone.utc) + wib_offset
                check_in_date = check_in_dt.date()

                # Cek apakah ada check_in lain pada tanggal yang sama
                existing_attendance = self.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('check_in', '>=', check_in_date.strftime('%Y-%m-%d 00:00:00')),
                    ('check_in', '<=', check_in_date.strftime('%Y-%m-%d 23:59:59')),
                    ('id', '!=', record.id)  # Hindari pengecekan terhadap record sendiri
                ], limit=1)

                if existing_attendance:
                    record.terlambat_detik = 0  # Jika sudah ada check-in pada hari yang sama, tidak dihitung keterlambat_detikan
                else:
                    # Konversi x_studio_work_from (float) ke waktu (HH:MM:SS)
                    work_from_hour = int(record.x_studio_work_from)
                    work_from_minute = int((record.x_studio_work_from - work_from_hour) * 60)
                    work_from_time = timedelta(hours=work_from_hour, minutes=work_from_minute)

                    # Ambil waktu dari check_in dan konversi ke timedelta dalam UTC+7
                    check_in_time = timedelta(hours=check_in_dt.hour, minutes=check_in_dt.minute, seconds=check_in_dt.second)

                    # Hitung selisih waktu dalam detik
                    terlambat_detik = (check_in_time - work_from_time).total_seconds()
                    record.terlambat_detik = max(int(terlambat_detik), 0)  # Jika terlambat_detik negatif (lebih awal), set ke 0
            else:
                record.terlambat_detik = 0
