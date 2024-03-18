{
    'name': 'iptech chatter_extension',
    'depends': [
        'base',
        'base_setup',
        "sale",
        "mail",
        "project",
        "task_tab_products"
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}