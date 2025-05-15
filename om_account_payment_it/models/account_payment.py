from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    name = fields.Char(string="Payment Name", readonly=True, copy=False, default="New")

    @api.model
    def _get_next_sequence(self, journal_code, year, month):
        """Menghasilkan nomor urut (3 digit) berdasarkan Payment Date (YY/MM)"""
        last_payment = self.search([
            ("name", "like", f"{journal_code} {year}/{month}/%")
        ], order="name desc", limit=1)

        if last_payment:
            try:
                last_number = int(last_payment.name[-3:])  # Ambil angka terakhir (XXX)
                return f"{last_number + 1:03d}"  # Tambah 1 dengan format 3 digit
            except ValueError:
                return "001"
        return "001"

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            journal = self.env['account.journal'].browse(vals.get('journal_id'))
            journal_code = journal.code if journal else 'XXX'

            # Ambil Payment Date
            payment_date = vals.get('date', fields.Date.context_today(self))
            if isinstance(payment_date, str):
                payment_date = fields.Date.from_string(payment_date)

            year = payment_date.strftime('%y')
            month = payment_date.strftime('%m')

            sequence = self._get_next_sequence(journal_code, year, month)
            vals['name'] = f"{journal_code} {year}/{month}/{sequence}"

        return super().create(vals)
