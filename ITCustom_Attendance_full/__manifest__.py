{
    'name': 'HR Attendance Custom',
    'version': '1.0',
    'summary': 'Menambahkan perhitungan terlambat pada hr.attendance',
    'description': 'Menambahkan field x_studio_terlambat_1 untuk menghitung selisih waktu terlambat.',
    'author': 'Your Name',
    'depends': ['hr_attendance'],
    'data': [
        'views/hr_attendance_views.xml',
    ],
    'installable': True,
    'application': False,
}