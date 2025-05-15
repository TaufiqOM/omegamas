from odoo import models, fields, api
import calendar, re


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_confirm(self):
        for order in self:
            date_start = order.date_start or fields.Date.today()
            year = date_start.year % 100
            month = date_start.month
            day = date_start.day

            picking_type_code = order.picking_type_id.sequence_code or 'XXX'

            # Cari sequence terakhir untuk tanggal yang sama
            existing_orders = self.env['mrp.production'].search([
                ('name', 'like', f"{picking_type_code} {year:02d}/{month:02d}/%")
            ], order="name desc", limit=1)
            
            if existing_orders:
                # Ambil angka urutan terakhir dengan regex
                match = re.search(r'(\d+)$', existing_orders.name)
                if match:
                    last_sequence = int(match.group(1)) + 1
                else:
                    last_sequence = 1
            else:
                last_sequence = 1

                # Format nomor sequence
            new_name = f"{picking_type_code} {year:02d}/{month:02d}/{last_sequence:03d}"

            order.name = new_name

        return super().action_confirm()

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()

        for production in self:
            if production.date_start:
                moves = self.env['account.move'].search([
                    ('stock_move_id', 'in', production.move_finished_ids.ids)
                ])

                for move in moves:
                    if move.state == 'posted':
                        move.button_draft()

                    move.name = False
                    move.date = production.date_start.date()

                    move_year = move.date.year % 100
                    move_month = move.date.month

                    picking_type_code = production.picking_type_id.sequence_code or 'XXX'

                    last_day = calendar.monthrange(move.date.year, move_month)[1]

                    sequence = 1
                    while True:
                        new_name = f"STJ/{picking_type_code} {move_year}/{move_month:02d}/{sequence:03d}"
                        existing = self.env['account.move'].search([('name', '=', new_name)], limit=1)
                        if not existing:
                            break
                        sequence += 1

                    move.name = new_name
                    move._compute_name()

                    if move.state == 'draft':
                        move.action_post()

                for move_line in production.move_raw_ids:
                    if move_line.date:
                        move_line.date = production.date_start.date()

                    account_moves = self.env['account.move'].search([
                        ('stock_move_id', '=', move_line.id)
                    ])

                    for account_move in account_moves:
                        if account_move.state == 'posted':
                            account_move.button_draft()

                        account_move.name = False
                        account_move.date = production.date_start.date()

                        move_year = account_move.date.year % 100
                        move_month = account_move.date.month

                        last_day = calendar.monthrange(account_move.date.year, move_month)[1]

                        sequence = 1
                        while True:
                            new_name = f"STJ/{picking_type_code} {move_year}/{move_month:02d}/{sequence:03d}"
                            existing = self.env['account.move'].search([('name', '=', new_name)], limit=1)
                            if not existing:
                                break
                            sequence += 1

                        account_move.name = new_name
                        account_move._compute_name()

                        if account_move.state == 'draft':
                            account_move.action_post()
        return res
