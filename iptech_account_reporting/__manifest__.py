{
    'name': 'iptech account_reporting',
    'depends': [
        'base',
        'base_setup',
        "sale",
        "account",
        "mail",
        'product', 'analytic', 'portal', 'digest'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_menus.xml'
    ],
    'installable': True,
    'application': True,
}