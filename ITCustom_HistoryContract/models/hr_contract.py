from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'

    history_ids = fields.One2many(
        'contract.history.employee',  # related model
        'contract_id',                # field di model tujuan (Many2one)
        string='History Records'
    )
    
    def action_update_history(self):
        for contract in self:
            # Ambil riwayat terakhir berdasarkan create_date (atau id, fallback)
            last_history = self.env['contract.history.employee'].search(
                [('contract_id', '=', contract.id)],
                order='create_date desc',  # Bisa juga 'id desc'
                limit=1
            )

            # Ambil data kontrak saat ini
            current_data = {
                'history_name': contract.name,
                'history_start_date': contract.date_start,
                'history_end_date': contract.date_end,
                'history_structure_type_id': contract.structure_type_id.id,
                'history_department_id': contract.department_id.id,
                'history_job_id': contract.job_id.id,
                'history_contract_type_id': contract.contract_type_id.id,
                'history_wage': contract.wage,
            }

            is_different = True  # Asumsikan beda

            if last_history:
                is_different = (
                    last_history.history_name != current_data['history_name'] or
                    last_history.history_start_date != current_data['history_start_date'] or
                    last_history.history_end_date != current_data['history_end_date'] or
                    (last_history.history_structure_type_id.id or False) != current_data['history_structure_type_id'] or
                    (last_history.history_department_id.id or False) != current_data['history_department_id'] or
                    (last_history.history_job_id.id or False) != current_data['history_job_id'] or
                    (last_history.history_contract_type_id.id or False) != current_data['history_contract_type_id'] or
                    last_history.history_wage != current_data['history_wage']
                )

            # Insert hanya jika data berbeda
            if is_different:
                self.env['contract.history.employee'].create({
                    'contract_id': contract.id,
                    **current_data
                })
