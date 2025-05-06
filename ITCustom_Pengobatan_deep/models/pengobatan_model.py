from odoo import models, fields, api

class Pengobatan(models.Model):
    _name = 'pengobatan.pengobatan'
    _description = 'Pengobatan Karyawan'
    
    name = fields.Char(string='Nomor', default='New')
    karyawan_id = fields.Many2one('hr.employee', string='Karyawan', required=True)
    tanggal_pengobatan = fields.Date(string='Tanggal', default=fields.Date.today)
    dokter = fields.Char(string='Dokter', required=True)
    klinik = fields.Char(string='Klinik/Rumah Sakit', required=True)
    diagnosa = fields.Text(string='Diagnosa')
    obat = fields.Text(string='Resep Obat')
    biaya = fields.Float(string='Biaya')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('paid', 'Paid')],
        default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pengobatan.pengobatan') or 'New'
        return super().create(vals)