from odoo import _, fields, models, api, exceptions
import logging
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """Override action_post untuk update ke AccountBankStatementLine"""
        for move in self:
            if not move.date:
                raise ValidationError(_("Date is required before posting the journal entry."))

        res = super().action_post()

        for move in self:
            # Jika journal_id adalah 1, gunakan format sequence SI YY/MM/XXX saat action_post
            if move.journal_id.id == 1:
                date_obj = move.date or fields.Date.today()
                move.name = self._generate_journal_sequence(date_obj, prefix='SI')

            if move.journal_id.id == 208:
                date_obj = move.date or fields.Date.today()
                move.name = self._generate_journal_sequence(date_obj, prefix='JP')
        return res

    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
             # Cek jika journal_id adalah 8, Inventory Valuation
            if vals.get('journal_id') == 8:
                # Jika accounting_date sudah ada di vals, Inventory Adjustment
                if vals.get('accounting_date'):
                    acc_date = fields.Date.from_string(vals['accounting_date'])
                    vals['date'] = acc_date
                    date_obj = acc_date
                    vals['name'] = self._generate_journal_sequence(date_obj, prefix='STJ')
                elif vals.get('stock_move_id'):
                    move = self.env['stock.move'].browse(vals['stock_move_id'])
                    quant = self.env['stock.quant'].search([
                        ('product_id', '=', move.product_id.id),
                        ('location_id', '=', move.location_id.id),
                        ('inventory_quantity_set', '=', True),
                    ], limit=1)
                    if quant and quant.accounting_date:
                        _logger.info(f"Found accounting_date from quant: {quant.accounting_date}")
                        vals['date'] = quant.accounting_date
                        date_obj = quant.accounting_date
                        vals['name'] = self._generate_journal_sequence(date_obj, prefix='STJ')
                    else:
                        _logger.warning("No accounting_date found from stock.move -> quant.")
                else:
                    # Jika accounting_date tidak ada, kita coba ambil tanggal dari related stock.picking manufacture
                    stock_picking = None
    
                    stock_picking_id = vals.get('stock_picking_id')
                    if stock_picking_id:
                        stock_picking = self.env['stock.picking'].browse(stock_picking_id)
    
                    if not stock_picking and vals.get('ref'):
                        stock_picking = self.env['stock.picking'].search([('name', '=', vals['ref'].split(' - ')[0])],
                                                                         limit=1)
    
                    if not stock_picking and vals.get('invoice_origin'):
                        stock_picking = self.env['stock.picking'].search([('name', '=', vals['invoice_origin'])], limit=1)
    
                    if stock_picking and stock_picking.scheduled_date:
                        scheduled_date = stock_picking.scheduled_date + timedelta(hours=7)
                        vals['date'] = scheduled_date.date()
                    elif 'invoice_date' in vals:
                        vals['date'] = vals['invoice_date']
                    else:
                        now_utc7 = datetime.utcnow() + timedelta(hours=7)
                        vals['date'] = now_utc7.date()

            # Cek jika journal_id adalah 207, gunakan format sequence JV YY/MM/XXX
            if vals.get('journal_id') == 207:
                date_obj = fields.Date.from_string(vals.get('date', fields.Date.today()))
                vals['name'] = self._generate_journal_sequence(date_obj, prefix='JV')

            # Cek jika journal_id adalah 1, gunakan format sequence SI YY/MM/XXX
            if vals.get('journal_id') == 1:
                date_obj = fields.Date.from_string(vals.get('date', fields.Date.today()))
                vals['name'] = self._generate_journal_sequence(date_obj, prefix='SI')

            # Jika journal_id.type adalah 'bank', gunakan format STJ/BNK1 YY/MM/XXX
            journal_id = vals.get('journal_id')
            if journal_id:
                journal = self.env['account.journal'].browse(journal_id)
                if journal.exists() and journal.type in ('bank', 'cash') and journal.code:
                    date_obj = fields.Date.from_string(vals.get('date', fields.Date.today()))
                    if journal.code:
                        prefix = f"STJ/{journal.code}"
                    else:
                        prefix = "STJ"

                    vals['name'] = self._generate_journal_sequence(date_obj, prefix=prefix)

        records = super().create(vals_list)
        return records

    def write(self, vals):
        if 'invoice_date' in vals and 'date' not in vals:
            if not self.date or self.date == self.invoice_date:
                vals['date'] = vals['invoice_date']
        return super().write(vals)

    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        """ Setting Accounting Date supaya sama dengan Bill Date ketika dirubah """
        if self.invoice_date:
            self.date = self.invoice_date

    def _generate_journal_sequence(self, date_obj, prefix):
        """Membuat sequence format Prefix YY/MM/XXX"""
        seq_prefix = f"{prefix} {date_obj.strftime('%y/%m')}/"
        last_entry = self.search([('name', 'like', seq_prefix)], order='name desc', limit=1)

        if last_entry and last_entry.name:
            last_number = int(last_entry.name.split('/')[-1]) + 1
        else:
            last_number = 1

        return f'{seq_prefix}{str(last_number).zfill(3)}'
