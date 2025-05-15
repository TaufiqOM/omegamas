from odoo import models, fields, api, SUPERUSER_ID
import logging
import re

_logger = logging.getLogger(__name__)

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    initial_date = fields.Date(string="Initial Date", help="Menyimpan tanggal awal sebelum diubah")

    @api.model
    def _get_next_sequence(self, year, month):
        """Menghasilkan nomor urut (3 digit) berdasarkan tahun & bulan untuk journal 209"""

        self.env.cr.execute("""
               SELECT name FROM account_move 
               WHERE name LIKE %s AND journal_id = %s
               ORDER BY name DESC LIMIT 1 FOR UPDATE
           """, (f"CSH {year}/{month}/%", 209))

        last_request = self.env.cr.fetchone()
        last_name = str(last_request[0]) if last_request and last_request[0] else None

        _logger.info(f"Last request found: {last_name if last_name else 'None'}")

        if last_name and re.match(r"CSH \d{2}/\d{2}/\d{3}", last_name):
            try:
                last_number = int(last_name[-3:])
                _logger.info(f"Last number parsed: {last_number}")  # Log nomor terakhir
                next_number = f"{last_number + 1:03d}"
                _logger.info(f"Next sequence generated: {next_number}")  # Log nomor baru
                return next_number
            except ValueError:
                _logger.warning(f"Gagal parsing nomor urut dari {last_name}")

        _logger.info("Returning default sequence: 001")
        return "001"

    def _get_custom_sequence(self, date):
        """Generate sequence hanya untuk journal 209"""
        year = date.strftime("%y")
        month = date.strftime("%m")
        sequence_number = self._get_next_sequence(year, month)
        return f"CSH {year}/{month}/{sequence_number}"

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info(f"Creating records with values: {vals_list}")
        st_lines = super().create(vals_list)

        for st_line in st_lines:
            if st_line.journal_id.id == 209 and st_line.date: # Hanya ubah jurnal 209
                if not st_line.date:
                    _logger.warning(f"Record {st_line.id} tidak memiliki date!")
                    continue

                st_line.initial_date = st_line.date
                _logger.info(f"Processing record {st_line.id} with initial date {st_line.initial_date}")

                # if st_line.move_id and st_line.move_id.journal_id.id == 209:
                if st_line.move_id and st_line.move_id.journal_id.id == 209 and not st_line.move_id.name.startswith("CSH"):
                    custom_sequence = self._get_custom_sequence(st_line.initial_date)
                    _logger.info(
                        f"Updating account_move {st_line.move_id.id} with name={custom_sequence} and date={st_line.initial_date}")
                    if st_line.move_id.state == 'posted':
                        st_line.move_id.sudo().button_draft()
                    st_line.move_id.sudo().write({'name': custom_sequence, 'date': st_line.initial_date})
                    st_line.move_id.sudo().action_post()

        return st_lines

    def write(self, vals):
        _logger.info(f"Updating records {self.ids} with values: {vals}")

        if 'date' in vals:
            for record in self:
                if record.journal_id.id == 209:  # Hanya journal 209 yang diproses
                    old_date = record.date
                    new_date = vals['date']
                    _logger.info(f"Record {record.id} changing date from {old_date} to {new_date}")

                    # Jika tanggal tidak berubah, lewati
                    if old_date == new_date:
                        _logger.info(f"Skipping sequence update for record {record.id} because date is unchanged")
                        continue

                    record.initial_date = new_date
                    new_sequence = self._get_custom_sequence(new_date)

                    if record.move_id and record.move_id.journal_id.id == 209:
                        _logger.info(
                            f"Updating account_move {record.move_id.id} with name={new_sequence} and date={new_date}")
                        if record.move_id.state == 'posted':
                            record.move_id.sudo().button_draft()
                        record.move_id.sudo().write({'name': new_sequence, 'date': new_date})
                        record.move_id.sudo().action_post()

        return super().write(vals)

    def action_save_close(self):
        _logger.info(f"Executing action_save_close for records {self.ids}")

        for record in self:
            if record.journal_id.id == 209 and record.move_id and record.move_id.journal_id.id == 209:
                if record.initial_date:
                    new_sequence = self._get_custom_sequence(record.initial_date)
                    _logger.info(
                        f"Updating account_move {record.move_id.id} with name={new_sequence} and date={record.initial_date}"
                    )
                    if record.move_id.state == 'posted':
                        record.move_id.sudo().button_draft()
                    record.move_id.sudo().write({
                        'name': new_sequence,
                        'date': record.initial_date
                    })
                    record.move_id.sudo().action_post()
        return {'type': 'ir.actions.act_window_close'}

    def action_save_new(self):
        _logger.info(f"Executing action_save_new for records {self.ids}")

        for record in self:
            if record.journal_id.id == 209 and record.move_id and record.move_id.journal_id.id == 209:
                if record.initial_date:
                    new_sequence = self._get_custom_sequence(record.initial_date)
                    _logger.info(
                        f"Updating account_move {record.move_id.id} with name={new_sequence} and date={record.initial_date}"
                    )
                    if record.move_id.state == 'posted':
                        record.move_id.sudo().button_draft()
                    record.move_id.sudo().write({
                        'name': new_sequence,
                        'date': record.initial_date
                    })
                    record.move_id.sudo().action_post()

        action = self.env['ir.actions.act_window']._for_xml_id(
            'account_accountant.action_bank_statement_line_form_bank_rec_widget'
        )
        action['context'] = {'default_journal_id': self._context['default_journal_id']}
        return action