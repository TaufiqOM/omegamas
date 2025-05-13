# File: __manifest__.py
{
    'name': 'History Contract',
    'version': '1.0',
    'depends': ['hr_payroll', 'hr', 'hr_contract'],
    'author': 'Taufiqur Rahman',
    'category': 'Payroll',
    'summary': 'Menambahkan menu All Report di Attendance',
    'data': [
        'views/hr_history_contract_button.xml',
        'views/hr_history_contract_views.xml',
    ],
    'installable': True,
    'application': False,
}
