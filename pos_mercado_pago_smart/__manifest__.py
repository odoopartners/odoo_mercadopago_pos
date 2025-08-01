{
    'name': 'POS Mercado Pago Smart',
    'version': '18.0.1.0.6',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'summary': 'Add payment support to Chile',
    'description': """
Add payment support to Chile.
    """,
    'module_type': 'official',
    'category': 'Sales/Point of Sale',
    'depends': ['pos_mercado_pago'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/mp_access_token_views.xml',
        'views/pos_order_views.xml'
    ],
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
