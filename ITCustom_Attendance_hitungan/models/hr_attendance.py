from odoo import models, fields, api
import dateutil.tz
import datetime

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    terlambat = fields.Integer(
        string='Terlambat (Menit)',
        compute='_compute_terlambat',
        store=True
    )

    terlambat_display = fields.Char(
        string='Terlambat',
        compute='_compute_terlambat_display'
    )

    valid = fields.Integer(
        string='Valid',
        compute='_compute_valid',
        store=True,
        default=1
    )
    valid_out = fields.Integer(
        string='Valid Out',
        compute='_compute_valid_out',
        store=True,
        default=1
    )

    @api.depends('check_in', 'employee_id')
    def _compute_valid(self):
        for record in self:
            record.valid = 1  # Default to 1
            if record.check_in:
                check_in_local = record.check_in + datetime.timedelta(hours=7)
                check_in_date = check_in_local.date()
                
                # Cek jika sudah ada presensi di hari yang sama
                for rec in record.employee_id.attendance_ids:
                    if rec.id != record.id and rec.check_in:
                        rec_check_in_local = rec.check_in + datetime.timedelta(hours=7)
                        if rec_check_in_local.date() == check_in_date and rec.presensi == 1:
                            record.valid = 0
                            break
                        
    @api.depends('check_in', 'work_from', 'valid', 'presensi')
    def _compute_terlambat(self):
        for record in self:
            # Jika valid = 0, langsung set terlambat = 0
            if record.valid == 0:
                record.terlambat = 0
                continue
            
            # Jika valid = 1 dan presensi = 1, lakukan perhitungan keterlambatan
            if record.presensi == 1 and record.check_in and record.work_from:
                wib_timezone = dateutil.tz.gettz('Asia/Jakarta')
                check_in_date = record.check_in.astimezone(wib_timezone)
                work_from_hours = int(record.work_from)
                work_from_minutes = int((record.work_from - work_from_hours) * 60)
                work_from_time = check_in_date.replace(hour=work_from_hours, minute=work_from_minutes, second=0)

                if check_in_date > work_from_time:
                    delta = check_in_date - work_from_time
                    record.terlambat = int(delta.total_seconds() // 60)
                else:
                    record.terlambat = 0
            else:
                record.terlambat = 0


    # @api.depends('check_out', 'employee_id')
    # def _compute_valid_out(self):
    #     for record in self:
    #         record.valid_out = 0  # Default to 0
    #         if record.check_out:
    #             check_out_local = record.check_out + datetime.timedelta(hours=7)
    #             check_out_date = check_out_local.date()

    #             # Cek apakah belum ada pulang_dini_true di hari yang sama
    #             is_valid = True
    #             for rec in record.employee_id.attendance_ids:
    #                 if rec.id != record.id and rec.check_out:
    #                     rec_check_out_local = rec.check_out + datetime.timedelta(hours=7)
    #                     if rec_check_out_local.date() == check_out_date and rec.pulang_dini_true == 1:
    #                         is_valid = False
    #                         break
    #             if is_valid:
    #                 record.valid_out = 1

                        
    # @api.depends('check_out', 'work_from', 'valid_out', 'pulang_dini_true')
    # def _compute_terlambat(self):
    #     for record in self:
    #         # Jika valid_out = 0, langsung set terlambat = 0
    #         if record.valid_out == 0:
    #             record.terlambat = 0
    #             continue
            
    #         # Jika valid_out = 1 dan pulang_dini_true = 1, lakukan perhitungan keterlambatan
    #         if record.pulang_dini_true == 1 and record.check_out and record.work_from:
    #             wib_timezone = dateutil.tz.gettz('Asia/Jakarta')
    #             check_out_date = record.check_out.astimezone(wib_timezone)
    #             work_from_hours = int(record.work_from)
    #             work_from_minutes = int((record.work_from - work_from_hours) * 60)
    #             work_from_time = check_out_date.replace(hour=work_from_hours, minute=work_from_minutes, second=0)

    #             if check_out_date > work_from_time:
    #                 delta = check_out_date - work_from_time
    #                 record.terlambat = int(delta.total_seconds() // 60)
    #             else:
    #                 record.terlambat = 0
    #         else:
    #             record.terlambat = 0


