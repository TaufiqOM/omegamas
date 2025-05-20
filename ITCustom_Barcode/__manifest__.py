{
    'name': 'Barcode',
    'summary': 'App to manage and book meeting rooms.',
    'description': '''
        Manage meeting rooms, book schedules, and prevent double bookings.
    ''',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'license': 'LGPL-3', 
    'author': 'Taufiqur Rahman',
    'website': 'http://www.omegamas.com',
    'depends': ['base', 'sale', 'product'],
    'data': [
        
        'security/ir.model.access.csv',
        'views/alokasi_views.xml',
        'views/actions.xml',
        'views/menus.xml',
        'views/barcode_wizard_view.xml',
        'views/barcode_views.xml',
        # 'views/generate_barcode_wizard_view.xml',
    ],
    
    'installable': True,
    'application': True,

}
