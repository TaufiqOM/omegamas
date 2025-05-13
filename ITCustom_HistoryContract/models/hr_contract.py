# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_HistoryContract/models/hr_contract.py
from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'

    history_name = fields.Char(string="History Name", readonly=True)
    history_start_date = fields.Date(string="History Start Date", readonly=True)
    history_end_date = fields.Date(string="History End Date", readonly=True)

    def action_update_history(self):
        for record in self:
            record.write({
                'history_name': record.name,
                'history_start_date': record.date_start,
                'history_end_date': record.date_end,
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'History data has been updated',
                'sticky': False,
                'type': 'success',
            }
        }