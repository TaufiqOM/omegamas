from odoo import models, fields, api

class HrContractHistory(models.Model):
    _name = 'hr.contract.history'
    _description = 'History of HR Contract'

    contract_id = fields.Many2one('hr.contract', string="Contract", required=True)
    history_name = fields.Char(string="History Name")
    history_start_date = fields.Date(string="History Start Date")
    history_end_date = fields.Date(string="History End Date")

