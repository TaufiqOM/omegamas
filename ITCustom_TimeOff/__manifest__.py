{
    'name': 'Custom Time Off Report (All Employees)',
    'version': '1.0',
    'category': 'Human Resources',
    'depends': ['hr', 'hr_holidays'],
    'data': [
        'views/timeoff_report_view.xml',
    ],
    'installable': True,
}
