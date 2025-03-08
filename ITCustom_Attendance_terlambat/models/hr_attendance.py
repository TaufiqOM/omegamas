from odoo import models, fields, api
import dateutil.tz

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        string='Working Schedule',
        related='employee_id.resource_calendar_id',
        store=True
    )

    day_code = fields.Integer(
        string='Day Code',
        compute='_compute_day_code',
        store=True
    )
    
    work_from = fields.Float(
        string='Work From Float',
        compute='_compute_work_from',
        store=True
    )

    work_from_display = fields.Char(
        string='Work From',
        compute='_compute_work_from_display'
    )
    work_to = fields.Float(
        string='Work To Float',
        compute='_compute_work_to',
        store=True
    )

    work_to_display = fields.Char(
        string='Work To',
        compute='_compute_work_to_display'
    )
    terlambat = fields.Integer(
        string='Terlambat (Menit)',
        compute='_compute_terlambat',
        store=True
    )

    terlambat_display = fields.Char(
        string='Terlambat',
        compute='_compute_terlambat_display'
    )

    terlambat_count = fields.Integer(
        string='Terlambat Count',
        compute='_compute_terlambat_count',
        store=True
    )

    pulang_dini = fields.Integer(
        string='Pulang Dini (Menit)',
        compute='_compute_pulang_dini',
        store=True
    )

    pulang_dini_display = fields.Char(
        string='Pulang Dini',
        compute='_compute_pulang_dini_display'
    )

    pulang_dini_count = fields.Integer(
        string='Pulang Dini Count',
        compute='_compute_pulang_dini_count',
        store=True
    )

    @api.depends('check_in')
    def _compute_day_code(self):
        wib_timezone = dateutil.tz.gettz('Asia/Jakarta')
        
        for record in self:
            if record.check_in:
                check_in_date = record.check_in.astimezone(wib_timezone)
                record.day_code = check_in_date.weekday()  # 0=Senin, ..., 6=Minggu
            else:
                record.day_code = 0

    @api.depends('day_code', 'calendar_id')
    def _compute_work_from(self):
        for record in self:
            if record.calendar_id:
                attendance = self.env['resource.calendar.attendance'].search([
                    ('calendar_id', '=', record.calendar_id.id),
                    ('dayofweek', '=', str(record.day_code)),
                    ('day_period', '=', 'morning')
                ], limit=1)
                record.work_from = attendance.hour_from if attendance else 0.0
            else:
                record.work_from = 0.0

    @api.depends('work_from')
    def _compute_work_from_display(self):
        for record in self:
            hours = int(record.work_from)
            minutes = int((record.work_from - hours) * 60)
            record.work_from_display = f"{hours:02}:{minutes:02}"
    @api.depends('day_code', 'calendar_id')

    def _compute_work_to(self):
        for record in self:
            if record.calendar_id:
                attendance = self.env['resource.calendar.attendance'].search([
                    ('calendar_id', '=', record.calendar_id.id),
                    ('dayofweek', '=', str(record.day_code)),
                    ('day_period', '=', 'afternoon')
                ], limit=1)
                record.work_to = attendance.hour_to if attendance else 0.0
            else:
                record.work_to = 0.0

    @api.depends('work_to')
    def _compute_work_to_display(self):
        for record in self:
            hours = int(record.work_to)
            minutes = int((record.work_to - hours) * 60)
            record.work_to_display = f"{hours:02}:{minutes:02}"

    @api.depends('check_in', 'work_from', 'employee_id')
    def _compute_terlambat(self):
        wib_timezone = dateutil.tz.gettz('Asia/Jakarta')
        
        for record in self:
            if record.check_in and record.work_from:
                check_in_date = record.check_in.astimezone(wib_timezone)
                work_from_hours = int(record.work_from)
                work_from_minutes = int((record.work_from - work_from_hours) * 60)
                work_from_time = check_in_date.replace(hour=work_from_hours, minute=work_from_minutes, second=0)
                
                # Mencari semua absensi pada hari tersebut untuk karyawan yang sama
                attendance_records = self.env['hr.attendance'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('check_in', '>=', check_in_date.date().strftime('%Y-%m-%d 00:00:00')),
                    ('check_in', '<', check_in_date.date().strftime('%Y-%m-%d 23:59:59'))
                ], order='check_in ASC')

                # Jika ada check-in pertama dan check-in kedua
                first_check_in = attendance_records.filtered(lambda r: r.check_in == min(attendance_records.mapped('check_in')))
                second_check_in = attendance_records.filtered(lambda r: r.check_in != first_check_in.check_in)

                if first_check_in and not second_check_in:  # Tidak ada check-in kedua
                    # Jika check-in pertama lebih dari waktu kerja, hitung keterlambatan
                    if check_in_date > work_from_time:
                        delta = check_in_date - work_from_time
                        record.terlambat = int(delta.total_seconds() // 60)
                    else:
                        record.terlambat = 0
                else:  # Ada check-in kedua
                    record.terlambat = 0
            else:
                record.terlambat = 0

    @api.depends('terlambat')
    def _compute_terlambat_display(self):
        for record in self:
            if record.terlambat:
                hours = record.terlambat // 60
                minutes = record.terlambat % 60
                record.terlambat_display = f"{hours:02}:{minutes:02}"
            else:
                record.terlambat_display = "00:00"

    @api.depends('check_out', 'work_to', 'employee_id')
    def _compute_pulang_dini(self):
        wib_timezone = dateutil.tz.gettz('Asia/Jakarta')

        for record in self:
            if record.check_out and record.work_to:
                check_out_date = record.check_out.astimezone(wib_timezone)
                work_to_hours = int(record.work_to)
                work_to_minutes = int((record.work_to - work_to_hours) * 60)
                work_to_time = check_out_date.replace(hour=work_to_hours, minute=work_to_minutes, second=0)
                
                # Mencari semua absensi pada hari tersebut untuk karyawan yang sama
                attendance_records = self.env['hr.attendance'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('check_out', '>=', check_out_date.date().strftime('%Y-%m-%d 00:00:00')),
                    ('check_out', '<', check_out_date.date().strftime('%Y-%m-%d 23:59:59'))
                ], order='check_out DESC')

                # Jika ada check-out pertama dan check-out kedua
                last_check_out = attendance_records.filtered(lambda r: r.check_out == max(attendance_records.mapped('check_out')))
                second_last_check_out = attendance_records.filtered(lambda r: r.check_out != last_check_out.check_out)

                if last_check_out and not second_last_check_out:  # Tidak ada check-out kedua
                    # Jika check-out terakhir lebih awal dari waktu pulang, hitung pulang dini
                    if check_out_date < work_to_time:
                        delta = work_to_time - check_out_date
                        record.pulang_dini = int(delta.total_seconds() // 60)
                    else:
                        record.pulang_dini = 0
                else:  # Ada check-out kedua
                    record.pulang_dini = 0
            else:
                record.pulang_dini = 0

    @api.depends('pulang_dini')
    def _compute_pulang_dini_display(self):
        for record in self:
            if record.pulang_dini:
                hours = record.pulang_dini // 60
                minutes = record.pulang_dini % 60
                record.pulang_dini_display = f"{hours:02}:{minutes:02}"
            else:
                record.pulang_dini_display = "00:00"

    @api.depends('terlambat')
    def _compute_terlambat_count(self):
        for record in self:
            record.terlambat_count = 1 if record.terlambat > 0 else 0

    @api.depends('pulang_dini')
    def _compute_pulang_dini_count(self):
        for record in self:
            record.pulang_dini_count = 1 if record.pulang_dini > 0 else 0