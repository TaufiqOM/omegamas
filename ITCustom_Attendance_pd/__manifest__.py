# File: __manifest__.py
{
    'name': 'Custom Attendance Report',
    'version': '1.0',
    'depends': ['hr_attendance'],
    'author': 'Muhammad Tajuddin',
    'category': 'Human Resources',
    'summary': 'Menambahkan menu All Report di Attendance',
    'data': [
        'views/hr_attendance_menu.xml',
    ],
    'installable': True,
    'application': False,
}