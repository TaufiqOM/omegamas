from odoo import models, api, fields

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def create(self, vals):
        leave = super(HrLeave, self).create(vals)
        if leave.state == 'validate':
            leave._force_clean_work_entry()
        return leave

    def write(self, vals):
        res = super(HrLeave, self).write(vals)
        if 'state' in vals and vals['state'] == 'validate':
            self._force_clean_work_entry()
        return res

    def _force_clean_work_entry(self):
        for leave in self:
            # Cari semua work entry bentrok
            domain = [
                ('employee_id', '=', leave.employee_id.id),
                ('date_start', '<', leave.date_to),
                ('date_stop', '>', leave.date_from),
                ('state', '=', 'draft'),
            ]
            conflict_entries = self.env['hr.work.entry'].search(domain)

            for entry in conflict_entries:
                entry_start = entry.date_start
                entry_stop = entry.date_stop
                leave_start = leave.date_from
                leave_stop = leave.date_to

                if leave_start <= entry_start and leave_stop >= entry_stop:
                    # Leave nutup semua: hapus entry
                    entry.unlink()
                elif leave_start <= entry_start < leave_stop < entry_stop:
                    # Potong awal
                    entry.date_start = leave_stop
                elif entry_start < leave_start < entry_stop <= leave_stop:
                    # Potong akhir
                    entry.date_stop = leave_start
                elif entry_start < leave_start and entry_stop > leave_stop:
                    # Split entry
                    self.env['hr.work.entry'].create({
                        'employee_id': entry.employee_id.id,
                        'work_entry_type_id': entry.work_entry_type_id.id,
                        'date_start': leave_stop,
                        'date_stop': entry_stop,
                        'state': 'draft',
                        'contract_id': entry.contract_id.id,
                    })
                    entry.date_stop = leave_start

            # Hapus attendance yang bentrok dengan cuti
            attendance_domain = [
                ('employee_id', '=', leave.employee_id.id),
                ('check_in', '>=', leave.date_from),
                ('check_out', '<=', leave.date_to),
                ('check_out', '>', leave.date_from),
            ]
            attendance_entries = self.env['hr.attendance'].search(attendance_domain)
            for attendance in attendance_entries:
                attendance.unlink()  # Hapus attendance yang bentrok
