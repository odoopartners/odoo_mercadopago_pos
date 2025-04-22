{
    'name': 'POS mercado pago extended',
    'version': '18.0.1.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'summary': 'Add payment support to Chile, Argentina and Brasil',
    'description': """
Add payment support to Chile, Argentina and Brasil.
    """,
    'module_type': 'official',
    'category': 'Sales/Point of Sale',
    'depends': ['pos_mercado_pago'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_mercado_pago_smart/static/**/*',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00,
}
