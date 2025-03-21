from odoo import models, fields, api
import calendar

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    name = fields.Char(string="Reference", readonly=True, copy=False, default='Draft')

    @api.model
    def create(self, vals):
        vals['name'] = 'Draft'
        return super(MrpProduction, self).create(vals)

    def action_confirm(self):
        for order in self:
            if order.name == 'Draft':  
                date_start = order.date_start or fields.Date.today()  
                year = date_start.year  
                month = date_start.month  

                picking_type_code = order.picking_type_id.sequence_code or 'XXX'

                last_day = calendar.monthrange(year, month)[1]  

                sequence = 1
                while True:
                    new_name = f"STRG/{picking_type_code} {year % 100}/{month:02d}/{sequence:03d}"
                    existing = self.env['mrp.production'].search([('name', '=', new_name)], limit=1)
                    if not existing:
                        break
                    sequence += 1  

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
