# models/hr_attendance.py
from odoo import models, fields, api

def generate_durasi_selection():
    selections = []
    for hour in range(0, 24):
        for minute in (0, 15, 30, 45):
            total_minutes = hour * 60 + minute
            label = f"{hour:02d}:{minute:02d}"
            selections.append((str(total_minutes), label))
    return selections

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    keterangan_selection = fields.Selection(
        selection=[
            ('EAO', 'EAO'),
            ('PD', 'PD'),
            ('MP', 'MP'),
            ('MSH', 'MSH'),
            ('MPD', 'MPD'),
        ],
        string='Keterangan'
    )
    durasi = fields.Selection(
        selection=generate_durasi_selection(),
        string='Durasi',
        help='Durasi waktu dalam format menit'
    )
    durasi_menit = fields.Integer(
        string='Durasi Menit', 
        compute='_compute_durasi_menit', 
        store=True
    )

    @api.depends('durasi')
    def _compute_durasi_menit(self):
        for record in self:
            record.durasi_menit = int(record.durasi) if record.durasi else 0