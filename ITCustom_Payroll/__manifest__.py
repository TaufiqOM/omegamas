# File: __manifest__.py
{
    'name': 'Custom Attendance Report',
    'version': '1.0',
    'depends': ['hr_payroll', 'hr', 'hr_contract'],
    'author': 'Taufiqur Rahman',
    'category': 'Payroll',
    'summary': 'Menambahkan menu All Report di Attendance',
    'data': [
        'views/hr_payroll.xml',
        'views/hr_salary_attachment.xml',
        'views/hr_contract.xml',
    ],
    'installable': True,
    'application': False,
}