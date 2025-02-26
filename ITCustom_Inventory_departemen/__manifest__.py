{
    'name': 'Custom Stock Valuation Editable',
    'version': '1.0',
    'author': 'Taufiqur Rahman',
    'category': 'Inventory',
    'summary': 'Mengizinkan pengeditan field name pada Stock Valuation (account.move)',
    'depends': ['purchase', 'hr'],
    'data': [
        'views/account_move_line_views.xml',
    ],
    'installable': True,
    'application': False,
}
