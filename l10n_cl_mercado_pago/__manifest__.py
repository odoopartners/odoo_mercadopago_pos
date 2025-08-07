{
    'name': 'L10N CL - POS Mercado Pago Smart',
    'version': '18.0.1.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'summary': 'Add payment support to Chile POS',
    'description': "Add payment support to Chile POS.",
    'module_type': 'official',
    'category': 'Sales/Point of Sale',
    'depends': [
        'l10n_cl_edi_pos',
        'pos_mercado_pago_smart'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'l10n_cl_mercado_pago/static/**/*',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00,
}
