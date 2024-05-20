{
    'name': 'iptech prorateo',
    'depends': [
        'base_setup',
        "sale",
        "account",
        "mail"
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/project_edit.xml',
        'views/sale_order_views.xml'
    ],
    'installable': True,
    'application': True,
}