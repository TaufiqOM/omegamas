{
    'name': 'IT Custom Public Kiosk - Final Solution',
    'version': '2.0.0',
    'summary': 'Force override kiosk text',
    'depends': ['hr_attendance'],
    'assets': {
        'web.assets_frontend': [
            'ITCustom_Public_Kiosk/static/src/css/kiosk_style.css',
            'ITCustom_Public_Kiosk/static/src/js/kiosk_override.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}