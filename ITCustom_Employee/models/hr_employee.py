from odoo import models, fields

class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_type = fields.Selection(
        selection_add=[
            ('staff', 'Staff'),
            ('magang', 'Magang'),
            ('konsultan', 'Konsultan')
        ],
        ondelete={'staff': 'set default', 'magang': 'set default', 'konsultan': 'set default'}
    )

    npwp = fields.Char(
    string="NPWP",
    store=True
    )

    agama = fields.Char(
        string="Agama",
        store=True
    )

    mulai_bergabung = fields.Date(
        string="Mulai Bergabung",
        store=True
    )