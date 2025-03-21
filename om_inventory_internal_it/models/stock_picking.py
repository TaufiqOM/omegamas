from odoo import models, fields, api
import calendar
from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    name = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default=lambda self: f"Draft/{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == 'Draft':
            vals['name'] = f"Draft/{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return super(StockPicking, self).create(vals)

    def button_validate(self):
        # 1. Update nomor picking jika internal dan masih berstatus Draft
        for picking in self:
            if picking.picking_type_id.code == 'internal' and picking.name.startswith('Draft'):
                date_scheduled = picking.scheduled_date or fields.Date.today()
                year = date_scheduled.year
                month = date_scheduled.month

                last_day = calendar.monthrange(year, month)[1]
                sequence = self.env['stock.picking'].search_count([
                    ('scheduled_date', '>=', f"{year}-{month:02d}-01"),
                    ('scheduled_date', '<=', f"{year}-{month:02d}-{last_day:02d}"),
                    ('state', '!=', 'draft')
                ]) + 1

                picking.name = f"STRG/INT/ {year % 100}/{month:02d}/{sequence:03d}"

        # 2. Lakukan validasi picking standar
        res = super(StockPicking, self).button_validate()

        # 3. Update field date dan regenerate sequence number pada account.move agar sesuai dengan scheduled_date picking
        for picking in self:
            if picking.picking_type_id.code == 'internal':
                # Cari semua stock.move yang terkait dengan picking ini
                stock_moves = self.env['stock.move'].search([('picking_id', '=', picking.id)])
                # Cari account.move yang terkait dengan stock.move tersebut
                moves = self.env['account.move'].search([
                    ('stock_move_id', 'in', stock_moves.ids)
                ])
                for move in moves:
                    # Jika move berstatus posted, set ke draft terlebih dahulu
                    if move.state == 'posted':
                        move.button_draft()

                    # Tentukan tanggal baru: ambil dari scheduled_date picking jika ada, atau gunakan hari ini
                    if picking.scheduled_date:
                        new_date = picking.scheduled_date.date() if isinstance(picking.scheduled_date, datetime) else picking.scheduled_date
                    else:
                        new_date = fields.Date.today()
                    move.date = new_date

                    # Clear sequence number agar bisa di-generate ulang
                    move.name = False

                    # Generate sequence baru yang sesuai dengan tanggal baru
                    move_year = new_date.year % 100
                    move_month = new_date.month

                    # Misal kode picking untuk internal adalah 'INT'
                    picking_code = 'INT'

                    # Hitung sequence berdasarkan account.move dengan tanggal yang sama (misalnya, di bulan yang sama)
                    last_day = calendar.monthrange(new_date.year, new_date.month)[1]
                    seq_count = self.env['account.move'].search_count([
                        ('date', '>=', f"{new_date.year}-{new_date.month:02d}-01"),
                        ('date', '<=', f"{new_date.year}-{new_date.month:02d}-{last_day:02d}"),
                        ('id', '!=', move.id)
                    ]) + 1

                    new_name = f"STJ/{picking_code} {move_year}/{move_month:02d}/{seq_count:03d}"
                    move.name = new_name
                    move._compute_name()

                    # Setelah regenerate, post kembali jika move masih dalam keadaan draft
                    if move.state == 'draft':
                        move.action_post()
        return res
