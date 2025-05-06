from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PengobatanKlaim(models.Model):
    _name = 'pengobatan.klaim'
    _description = 'Pengobatan Klaim'

    name = fields.Char(string='Deskripsi Klaim', compute='_compute_name', store=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Nama Karyawan',
        required=True,
        domain=lambda self: self._get_employee_domain()
    )
    nominal = fields.Float(string='Nominal')
    keterangan = fields.Text(string='Keterangan')
    tanggal_klaim = fields.Date(string='Tanggal Klaim')

    upload_file = fields.Binary("Upload File")
    filename = fields.Char("Filename")

    is_image = fields.Boolean("Is Image", compute="_compute_file_type", store=True)
    is_pdf = fields.Boolean("Is PDF", compute="_compute_file_type", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('employee_id', 'tanggal_klaim')
    def _compute_name(self):
        for record in self:
            if record.employee_id and record.tanggal_klaim:
                record.name = f"{record.employee_id.name} - {record.tanggal_klaim}"
            else:
                record.name = 'Klaim Tidak Lengkap'

    @api.depends('filename')
    def _compute_file_type(self):
        for record in self:
            if record.filename:
                ext = record.filename.lower().split('.')[-1]
                record.is_image = ext in ['jpg', 'jpeg', 'png', 'gif']
                record.is_pdf = ext == 'pdf'
            else:
                record.is_image = False
                record.is_pdf = False

    @api.model
    def _get_employee_domain(self):
        employee_ids = self.env['pengobatan.alokasi'].search([]).mapped('employee_id.id')
        return [('id', 'in', employee_ids)]

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'

    def action_paid(self):
        for rec in self:
            rec.state = 'paid'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'
    def action_cancel(self):  # Added cancel action
        for rec in self:
            rec.state = 'cancel'

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise UserError("You can only delete records with status 'Draft' or 'Cancelled'.")
        return super(PengobatanKlaim, self).unlink()
    
    @api.model
    def _get_employee_domain(self):
        employee_ids = self.env['pengobatan.alokasi'].search([]).mapped('employee_id.id')
        return [('id', 'in', employee_ids)]

    @api.constrains('employee_id', 'tanggal_klaim', 'nominal')
    def _check_valid_alokasi_and_nominal(self):
        Alokasi = self.env['pengobatan.alokasi']
        for rec in self:
            if not rec.employee_id or not rec.tanggal_klaim:
                continue

            # Cari alokasi yang cocok untuk karyawan dan tanggal klaim
            alokasis = Alokasi.search([
                ('employee_id', '=', rec.employee_id.id),
                ('berlaku_mulai', '<=', rec.tanggal_klaim),
                ('berlaku_sampai', '>=', rec.tanggal_klaim),
            ])

            if not alokasis:
                raise ValidationError("Tidak ada alokasi pengobatan yang valid untuk karyawan ini pada tanggal klaim.")

            alokasi_valid = alokasis[0]  # Ambil alokasi pertama yang cocok
            # Hitung total klaim 'paid' untuk alokasi ini
            total_klaim = sum(self.env['pengobatan.klaim'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'paid'),
                ('tanggal_klaim', '>=', alokasi_valid.berlaku_mulai),
                ('tanggal_klaim', '<=', alokasi_valid.berlaku_sampai),
                ('id', '!=', rec.id),  # Hindari menjumlahkan diri sendiri jika sedang diupdate
            ]).mapped('nominal'))

            sisa = alokasi_valid.jatah_pengobatan - total_klaim

            if sisa < rec.nominal:
                raise ValidationError("Sisa pengobatan tidak mencukupi untuk klaim ini.")