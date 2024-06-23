{
    'name': 'iptech contact office',
    'depends': [
        'base',
        'base_setup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml'
    ],
    'installable': True,
    'application': True,
}