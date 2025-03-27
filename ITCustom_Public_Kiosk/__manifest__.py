{
    'name': 'Custom Attendance Gantt',
    'version': '1.0',
    'summary': 'Modify Gantt view for Attendance to use work_from and work_to',
    'author': 'Taufiqur Rahman',
    'category': 'Human Resources',
    'license': 'LGPL-3',
    'depends': ['hr_attendance', 'hr_attendance_gantt'],
    'data': [
        'views/hr_attendance_gantt_view.xml',
    ],
    'installable': True,
    'application': False,
}
